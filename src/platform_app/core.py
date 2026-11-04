"""Coleta, persistência e geração factual dos dossiês de vaga."""
import copy
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from src.opportunities.tracker import load_policy, score
from . import sources


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_STATUS = {"nova", "avaliar", "candidatada", "descartada"}


def paths(person):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", person):
        raise ValueError("Perfil inválido")
    return ROOT / "input" / person, ROOT / "outputs" / person / "platform"


def config(person):
    private, output = paths(person)
    private.mkdir(parents=True, exist_ok=True)
    private.chmod(0o700)
    data = json.loads((private / "platform.json").read_text(encoding="utf-8"))
    if data.get("person") != person:
        raise ValueError("platform.json deve indicar o mesmo perfil")
    for key in ("greenhouse_boards", "lever_sites"):
        if not isinstance(data.get(key, []), list):
            raise ValueError(f"{key} deve ser uma lista")
    maximum = data.get("max_new_documents_per_run", 10)
    if not isinstance(maximum, int) or isinstance(maximum, bool) or not 0 <= maximum <= 30:
        raise ValueError("max_new_documents_per_run deve estar entre 0 e 30")
    return private, output, data, load_policy(private / "job_policy.json")


def database(output):
    output.mkdir(parents=True, exist_ok=True)
    output.chmod(0o700)
    db_file = output / "jobs.sqlite3"
    con = sqlite3.connect(db_file, timeout=30)
    db_file.chmod(0o600)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, url TEXT NOT NULL UNIQUE, source TEXT NOT NULL,
        title TEXT NOT NULL, company TEXT NOT NULL, location TEXT NOT NULL,
        description TEXT NOT NULL, score INTEGER NOT NULL, eligible INTEGER NOT NULL,
        reasons TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'nova',
        first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, generated_at TEXT,
        generation_error TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT ''
    )""")
    con.commit()
    return con


def normalize_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL de vaga inválida")
    return parsed._replace(query="", fragment="").geturl().rstrip("/")


def geography_ok(location):
    text = location.casefold()
    positive = ("brasil", "brazil", "latam", "latin america", "worldwide", "global", "anywhere")
    if any(x in text for x in positive):
        return True
    return not bool(re.search(r"\b(usa?|united states|canada|europe|european union|uk|united kingdom|australia)\b", text))


def import_jobs(con, jobs, policy):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    inserted = 0
    for item in jobs:
        try:
            url = normalize_url(item["url"])
        except (KeyError, ValueError):
            continue
        if not item.get("title"):
            continue
        match = score(item, policy)
        identity = hashlib.sha256(url.encode()).hexdigest()[:20]
        country_ok = geography_ok(item["location"])
        reason = ", ".join(match["titles"] + match["skills"])
        if not country_ok:
            reason += "; restrição geográfica a confirmar"
        exists = con.execute("SELECT id FROM jobs WHERE id=?", (identity,)).fetchone()
        con.execute("""INSERT INTO jobs
            (id,url,source,title,company,location,description,score,eligible,reasons,first_seen,last_seen)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET source=excluded.source,title=excluded.title,
                company=excluded.company,location=excluded.location,
                description=excluded.description,score=excluded.score,
                eligible=excluded.eligible,reasons=excluded.reasons,last_seen=excluded.last_seen""",
            (identity, url, item["source"], item["title"], item["company"],
             item["location"], item["description"], match["score"],
             int(match["eligible"] and country_ok), reason, now, now))
        inserted += not bool(exists)
    con.commit()
    return inserted


def relevance(text, terms):
    lower = text.casefold()
    return sum(term.casefold() in lower for term in terms)


def adapt_resume(base, row, policy):
    """Seleciona/reordena APENAS fatos do currículo mestre; não inventa conquistas."""
    result = copy.deepcopy(base)
    description = (row["title"] + " " + row["description"]).casefold()
    terms = [t for t in policy["skills"] + policy["titles"] if t.casefold() in description]
    for item in result.get("work", []):
        highlights = item.get("highlights", [])
        item["highlights"] = sorted(highlights, key=lambda h: -relevance(h, terms))
    result["skills"] = sorted(result.get("skills", []),
                              key=lambda s: -relevance(" ".join(s.get("keywords", [])), terms))
    evidence = " ".join(
        [result.get("basics", {}).get("summary", "")] +
        [h for work in result.get("work", []) for h in work.get("highlights", [])] +
        [word for skill in result.get("skills", []) for word in skill.get("keywords", [])]
    )
    verified = [term for term in terms if term.casefold() in evidence.casefold()]
    if verified:
        original = result["basics"].get("summary", "").strip().rstrip(".")
        result["basics"]["summary"] = (
            original + ". " if original else ""
        ) + "Experiência documentada relacionada a esta vaga: " + ", ".join(verified[:5]) + "."
    # Cargo, empresas, datas, formação e fatos das experiências permanecem intactos.
    return result, terms


def interview_script(resume, row, terms):
    highlights = [(work.get("name", ""), work.get("position", ""), highlight)
                  for work in resume.get("work", []) for highlight in work.get("highlights", [])]
    highlights.sort(key=lambda item: -relevance(item[2], terms))
    lines = [
        f"# Preparação para entrevista — {row['title']}", "",
        f"Empresa: {row['company'] or 'a confirmar'}", f"Vaga: {row['url']}", "",
        "Este roteiro usa apenas fatos do currículo mestre. Ajuste a fala com suas palavras e confira a vaga no site.", "",
        "## Abertura sugerida", "",
        f"Atuo como {resume['work'][0].get('position', 'profissional de tecnologia')} e trago experiência "
        f"descrita no meu currículo: {resume.get('basics', {}).get('summary', '').strip()}", "",
        "## Experiências para contar", ""
    ]
    if highlights:
        for index, (company, role, fact) in enumerate(highlights[:5], 1):
            lines += [f"{index}. **{company} — {role}:** {fact}",
                      "   Explique o contexto, sua ação, a validação e o resultado comprovável.", ""]
    else:
        lines += ["Seu currículo mestre ainda não contém experiências detalhadas.", ""]
    lines += ["## Perguntas para ensaiar", ""]
    for term in terms[:8]:
        proof = next((f"{company}: {fact}" for company, _, fact in highlights
                      if term.casefold() in fact.casefold()), None)
        lines.append(f"- **{term}:** {proof or 'Não há exemplo específico no currículo mestre. Confirme sua vivência antes de responder.'}")
    lines += ["", "## Pontos a confirmar antes de se candidatar", "",
              "- O trabalho é realmente 100% remoto e aceita profissionais no Brasil?",
              "- Quais requisitos são obrigatórios e quais são diferenciais?",
              "- Há tecnologias citadas na vaga que não aparecem no seu currículo? Não as apresente como experiência.", ""]
    return "\n".join(lines)


def generate(con, row, person, policy, output):
    source = ROOT / "data" / person / "resume.json"
    if not source.is_file():
        raise FileNotFoundError(f"Currículo mestre ausente: {source}")
    base = json.loads(source.read_text(encoding="utf-8"))
    if not base.get("basics", {}).get("name") or not base.get("work"):
        raise ValueError("O currículo mestre precisa de nome e experiências verificadas")
    adapted, terms = adapt_resume(base, row, policy)
    dest = output / "documents" / row["id"]
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "resume.json").write_text(json.dumps(adapted, ensure_ascii=False, indent=2), encoding="utf-8")
    (dest / "interview.md").write_text(interview_script(adapted, row, terms), encoding="utf-8")
    (dest / "job.json").write_text(json.dumps({key: row[key] for key in
        ("url", "title", "company", "location", "description")}, ensure_ascii=False, indent=2), encoding="utf-8")
    from resume.pdf_reportlab import generate_pdf
    # ReportLab interpreta marcação XML nos campos. Escape de dados não confiáveis só no PDF.
    pdf_data = copy.deepcopy(adapted)
    def safe(node):
        if isinstance(node, dict):
            return {k: safe(v) for k, v in node.items()}
        if isinstance(node, list):
            return [safe(v) for v in node]
        return escape(node) if isinstance(node, str) else node
    pdf_json = dest / "resume-pdf.json"
    pdf_json.write_text(json.dumps(safe(pdf_data), ensure_ascii=False), encoding="utf-8")
    try:
        generate_pdf(str(pdf_json), str(dest / "resume.pdf"))
    finally:
        pdf_json.unlink(missing_ok=True)
    con.execute("UPDATE jobs SET generated_at=?, generation_error='' WHERE id=?",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), row["id"]))
    con.commit()


def collect(private, settings):
    jobs, errors = [], []
    providers = []
    if settings.get("remotive"):
        providers.append(("Remotive", lambda: sources.remotive(private)))
    if settings.get("arbeitnow"):
        providers.append(("Arbeitnow", sources.arbeitnow))
    for name in settings.get("greenhouse_boards", []):
        providers.append((f"Greenhouse/{name}", lambda name=name: sources.greenhouse(name)))
    for name in settings.get("lever_sites", []):
        providers.append((f"Lever/{name}", lambda name=name: sources.lever(name)))
    providers.append(("Arquivos locais", lambda: sources.local_alerts(private)))
    if settings.get("gmail_query"):
        providers.append(("Gmail", lambda: sources.gmail_alerts(private, settings["gmail_query"])))
    for name, function in providers:
        try:
            jobs.extend(function())
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
    return jobs, errors


def run(person):
    import fcntl
    private, output, settings, policy = config(person)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "run.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Uma coleta já está em execução") from exc
        return _run_unlocked(person, private, output, settings, policy)


def _run_unlocked(person, private, output, settings, policy):
    con = database(output)
    jobs, errors = collect(private, settings)
    added = import_jobs(con, jobs, policy)
    candidates = con.execute("""SELECT * FROM jobs WHERE eligible=1 AND generated_at IS NULL
        AND status != 'descartada' ORDER BY score DESC, first_seen DESC LIMIT ?""",
        (settings["max_new_documents_per_run"],)).fetchall()
    generated = 0
    for row in candidates:
        try:
            generate(con, row, person, policy, output)
            generated += 1
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"[:300]
            errors.append(f"Documento {row['id']}: {message}")
            con.execute("UPDATE jobs SET generation_error=? WHERE id=?", (message, row["id"]))
            con.commit()
    result = {"collected": len(jobs), "new": added, "generated": generated, "errors": errors,
              "completed_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (output / "last-run.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    con.close()
    return result
