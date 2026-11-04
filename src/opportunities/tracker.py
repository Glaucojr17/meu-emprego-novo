"""Importa alertas do próprio usuário e mantém um histórico verificável.

Nenhum comando acessa LinkedIn ou Gupy, envia currículo ou registra candidatura
sem que o usuário a tenha feito e fornecido um comprovante local.
"""

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from email import policy as email_policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse


URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
FIELDS = ("source", "url", "title", "company", "location", "description")


def canonical_url(value):
    """Aceita apenas links diretos reconhecíveis de vagas das duas plataformas."""
    try:
        url = urlparse(value.strip().rstrip(".,;)]}"))
        hostname = (url.hostname or "").lower()
        path = url.path.rstrip("/")
        if url.scheme != "https" or url.username or url.password or url.port:
            return None
        if hostname in {"linkedin.com", "www.linkedin.com"}:
            match = re.fullmatch(r"/jobs/view/(\d+)(?:/.*)?", path)
            if match:
                return f"https://www.linkedin.com/jobs/view/{match.group(1)}/"
        if hostname == "gupy.io" or hostname.endswith(".gupy.io"):
            match = re.fullmatch(r"/(?:jobs|job)/(\d+)(?:/.*)?", path)
            if match:
                return f"https://{hostname}/jobs/{match.group(1)}"
    except ValueError:
        return None
    return None


class JobLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.current = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = dict(attrs).get("href", "")
            self.text = []

    def handle_data(self, data):
        if self.current is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append((self.current, " ".join(" ".join(self.text).split())))
            self.current = None


def direct_url(value):
    """Alguns alertas usam um redirecionamento. Só segue parâmetro explícito de vaga."""
    direct = canonical_url(value)
    if direct:
        return direct
    try:
        query = parse_qs(urlparse(value).query)
        for key in ("url", "jobUrl", "job_url"):
            for target in query.get(key, []):
                direct = canonical_url(target)
                if direct:
                    return direct
    except ValueError:
        pass
    return None


def from_eml(path):
    return from_eml_bytes(path.read_bytes())


def from_eml_bytes(raw):
    message = BytesParser(policy=email_policy.default).parsebytes(raw)
    subject = str(message.get("subject", "Alerta de vaga"))[:200]
    results = []
    parts = message.walk() if message.is_multipart() else [message]
    for part in parts:
        if part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() == "text/html":
            parser = JobLinks()
            parser.feed(part.get_content())
            for link, label in parser.links:
                url = direct_url(link)
                if url:
                    results.append({"source": "alerta .eml", "url": url,
                                    "title": label[:200] or subject, "company": "",
                                    "location": "", "description": subject})
        elif part.get_content_type() == "text/plain":
            for raw in URL_RE.findall(part.get_content()):
                url = direct_url(raw)
                if url:
                    results.append({"source": "alerta .eml", "url": url,
                                    "title": subject, "company": "",
                                    "location": "", "description": ""})
    return results


def from_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not {"url", "title"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV precisa das colunas url e title")
        return [{field: (row.get(field) or "").strip() for field in FIELDS}
                for row in reader]


def load_policy(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("titles", "skills", "exclude"):
        if not isinstance(data.get(key), list) or not all(isinstance(x, str) for x in data[key]):
            raise ValueError(f"A política precisa da lista de textos '{key}'")
    if not isinstance(data.get("remote_only"), bool):
        raise ValueError("A política precisa do booleano 'remote_only'")
    return data


def score(job, preferences):
    title = job["title"].casefold()
    full = " ".join(str(job.get(field, "")) for field in FIELDS if field != "url").casefold()
    matched_titles = [word for word in preferences["titles"] if word.casefold() in title]
    matched_skills = [word for word in preferences["skills"] if word.casefold() in full]
    excluded = [word for word in preferences["exclude"] if word.casefold() in full]
    remote = any(word in full for word in ("remoto", "remote", "home office", "100% remoto"))
    # Sem localização ou regime explícito não se presume trabalho remoto.
    eligible = bool(matched_titles) and not excluded and (remote or not preferences["remote_only"])
    return {"score": 3 * len(matched_titles) + len(matched_skills) + (2 if remote else 0),
            "eligible": eligible, "titles": matched_titles, "skills": matched_skills,
            "excluded": excluded, "remote_evidence": remote}


def read_ledger(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Histórico inválido")
    return data


def save_ledger(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_report(output, jobs, ledger):
    output.mkdir(parents=True, exist_ok=True)
    with (output / "vagas.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["score", "elegivel", "status", "title", "company", "location", "url", "motivos"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for job in jobs:
            match = job["match"]
            writer.writerow({"score": match["score"], "elegivel": match["eligible"],
                             "status": ledger.get(job["url"], {}).get("status", "encontrada"),
                             "title": job["title"], "company": job["company"],
                             "location": job["location"], "url": job["url"],
                             "motivos": "; ".join(match["titles"] + match["skills"] + match["excluded"])})
    lines = ["# Triagem de vagas", "", "Aderência por palavras-chave; confirme regime, requisitos e empresa no anúncio.", ""]
    for job in jobs:
        match = job["match"]
        label = "Revisar" if match["eligible"] else "Pendente de comprovação/fora do filtro"
        status = ledger.get(job["url"], {}).get("status", "encontrada")
        lines += [f"## {job['title']}", "", f"- Link: {job['url']}",
                  f"- Triagem: {label} (pontuação {match['score']}); status: {status}",
                  f"- Evidências: {', '.join(match['titles'] + match['skills']) or 'insuficientes'}", ""]
    lines += ["## Candidaturas confirmadas", ""]
    confirmed = [(url, row) for url, row in ledger.items() if row.get("status") == "candidatada"]
    if not confirmed:
        lines.append("Nenhuma candidatura confirmada.")
    for url, row in sorted(confirmed):
        lines.append(f"- {row['date']}: {row['title']} — {url}; comprovante local: {row['evidence']}")
    (output / "relatorio.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def scan(args):
    preferences = load_policy(args.policy)
    jobs = {}
    for path in sorted(args.alerts.glob("*.eml")) if args.alerts.exists() else []:
        for job in from_eml(path):
            jobs[job["url"]] = job
    if args.csv and args.csv.exists():
        for job in from_csv(args.csv):
            url = canonical_url(job["url"])
            if url:
                job["url"] = url
                jobs[url] = job  # descrição informada manualmente tem prioridade
    ranked = []
    for job in jobs.values():
        job["match"] = score(job, preferences)
        ranked.append(job)
    ranked.sort(key=lambda row: (not row["match"]["eligible"], -row["match"]["score"], row["url"]))
    write_report(args.output, ranked, read_ledger(args.output / "historico.json"))
    print(f"{len(ranked)} vagas únicas; relatório: {args.output / 'relatorio.md'}")


def record(args):
    url = canonical_url(args.url)
    if not url:
        raise ValueError("Informe uma URL direta de vaga LinkedIn/Gupy")
    if not args.evidence.is_file():
        raise ValueError("O comprovante local da candidatura não existe")
    if args.evidence.resolve().is_relative_to(Path.cwd().resolve()) and not (
        args.evidence.resolve().is_relative_to((Path.cwd() / "input").resolve())
        or args.evidence.resolve().is_relative_to((Path.cwd() / "outputs").resolve())
    ):
        raise ValueError("Guarde o comprovante em input/ ou outputs/ para evitar publicação acidental")
    path = args.output / "historico.json"
    ledger = read_ledger(path)
    ledger[url] = {"status": "candidatada", "title": args.title,
                   "date": datetime.now(timezone.utc).date().isoformat(),
                   "evidence": str(args.evidence)}
    save_ledger(path, ledger)
    print(f"Candidatura registrada com comprovante: {url}. Rode scan novamente para atualizar o relatório.")


def main():
    parser = argparse.ArgumentParser(description="Triagem local de alertas e acompanhamento de candidaturas")
    parser.add_argument("--person", required=True, help="Pasta local de perfil, por exemplo glaucojunior")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan", help="Importa .eml e CSV local, sem acessar plataformas")
    submission = sub.add_parser("record", help="Registra candidatura já enviada por você")
    submission.add_argument("--url", required=True)
    submission.add_argument("--title", required=True)
    submission.add_argument("--evidence", type=Path, required=True, help="Print/recibo salvo em input/ ou outputs/")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.person):
        parser.error("Nome do perfil deve conter apenas letras, números, _ ou -")
    args.alerts = Path("input") / args.person / "job_alerts"
    args.csv = Path("input") / args.person / "vagas.csv"
    args.policy = Path("input") / args.person / "job_policy.json"
    args.output = Path("outputs") / args.person / "opportunities"
    try:
        if args.command == "scan":
            scan(args)
        else:
            record(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

