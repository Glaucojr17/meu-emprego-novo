"""Fontes permitidas: APIs públicas e alertas da própria caixa postal."""
import base64
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from src.opportunities.tracker import from_csv, from_eml


TOKEN = re.compile(r"^[a-zA-Z0-9_-]{1,80}$")
USER_AGENT = "GlaucoJobDesk/1.0 (personal job search; contact via repository)"


def fetch_json(url, domain):
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=20) as response:
        if urlparse(response.geturl()).hostname != domain:
            raise ValueError("Redirecionamento para outro domínio recusado")
        data = response.read(20_000_001)
        if len(data) > 20_000_000:
            raise ValueError("Resposta maior que o limite de 20 MB")
    return json.loads(data)


def clean_html(value):
    from html import unescape
    text = unescape(unescape(value or ""))
    return " ".join(re.sub(r"<[^>]+>", " ", text).split())[:20000]


def job(source, url, title, company, location, description):
    if not url or urlparse(url).scheme != "https" or not urlparse(url).hostname:
        return None
    return {"source": source, "url": url.strip(), "title": str(title or "").strip()[:220],
            "company": str(company or "").strip()[:160], "location": str(location or "").strip()[:160],
            "description": clean_html(str(description or ""))}


def remotive(base):
    cache = base / "remotive-cache.json"
    if cache.exists() and time.time() - cache.stat().st_mtime < 6 * 3600:
        data = json.loads(cache.read_text(encoding="utf-8"))
    else:
        data = fetch_json("https://remotive.com/api/remote-jobs", "remotive.com")
        cache.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        cache.chmod(0o600)
    return [j for row in data.get("jobs", []) if (j := job(
        "Remotive", row.get("url"), row.get("title"), row.get("company_name"),
        "Remoto — " + (row.get("candidate_required_location") or "confirmar país"),
        row.get("description"))) is not None]


def arbeitnow():
    data = fetch_json("https://www.arbeitnow.com/api/job-board-api", "www.arbeitnow.com")
    return [j for row in data.get("data", []) if row.get("remote") and (j := job(
        "Arbeitnow", row.get("url"), row.get("title"), row.get("company_name"),
        row.get("location") or "Remoto — confirmar país", row.get("description"))) is not None]


def greenhouse(board):
    if not TOKEN.fullmatch(board):
        raise ValueError("Token de board Greenhouse inválido")
    data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true",
                      "boards-api.greenhouse.io")
    return [j for row in data.get("jobs", []) if (j := job(
        "Greenhouse", row.get("absolute_url"), row.get("title"), board,
        (row.get("location") or {}).get("name"), row.get("content"))) is not None]


def lever(site):
    if not TOKEN.fullmatch(site):
        raise ValueError("Site Lever inválido")
    rows = fetch_json(f"https://api.lever.co/v0/postings/{site}?mode=json", "api.lever.co")
    return [j for row in rows if (j := job(
        "Lever", row.get("hostedUrl"), row.get("text"), site,
        (row.get("categories") or {}).get("location"),
        row.get("descriptionPlain") or row.get("description"))) is not None]


def local_alerts(base):
    items = []
    for path in sorted((base / "job_alerts").glob("*.eml")):
        items.extend(from_eml(path))
    path = base / "vagas.csv"
    if path.exists():
        items.extend(from_csv(path))
    return [j for row in items if (j := job(
        row.get("source") or "Alerta", row.get("url"), row.get("title"),
        row.get("company"), row.get("location"), row.get("description"))) is not None]


def gmail_alerts(base, query):
    """Credenciais OAuth Desktop locais; nenhum token é versionado."""
    if not query:
        return []
    from google.auth.transport.requests import Request as GoogleRequest
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from src.opportunities.tracker import from_eml_bytes

    token = base / "gmail-token.json"
    if not token.exists():
        raise FileNotFoundError("OAuth Gmail não configurado; rode auth-gmail primeiro")
    credentials = Credentials.from_authorized_user_file(
        str(token), ["https://www.googleapis.com/auth/gmail.readonly"])
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(GoogleRequest())
        token.write_text(credentials.to_json(), encoding="utf-8")
        token.chmod(0o600)
    if not credentials.valid:
        raise ValueError("Token Gmail inválido; renove a autorização")
    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    items, page = [], None
    for _ in range(5):  # máximo de 250 mensagens por execução
        result = service.users().messages().list(
            userId="me", q=query, maxResults=50, pageToken=page).execute()
        for msg in result.get("messages", []):
            raw = service.users().messages().get(userId="me", id=msg["id"], format="raw").execute()["raw"]
            items.extend(from_eml_bytes(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))))
        page = result.get("nextPageToken")
        if not page:
            break
    return [j for row in items if (j := job(
        "Alerta Gmail", row["url"], row["title"], row["company"],
        row["location"], row["description"])) is not None]


def authorize_gmail(base):
    from google_auth_oauthlib.flow import InstalledAppFlow
    source = base / "google-credentials.json"
    if not source.exists():
        raise FileNotFoundError(f"Salve o OAuth Desktop JSON em {source}")
    flow = InstalledAppFlow.from_client_secrets_file(
        str(source), ["https://www.googleapis.com/auth/gmail.readonly"])
    credentials = flow.run_local_server(host="127.0.0.1", port=8765, open_browser=False)
    token = base / "gmail-token.json"
    token.write_text(credentials.to_json(), encoding="utf-8")
    token.chmod(0o600)
    return token
