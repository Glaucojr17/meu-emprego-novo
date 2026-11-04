"""Painel privado: bind local + túnel SSH, autenticação e CSRF nos formulários."""
import html
import hashlib
import os
import re
import secrets
from urllib.parse import parse_qs
from starlette.concurrency import run_in_threadpool

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .core import ALLOWED_STATUS, config, database, generate, paths, run


app = FastAPI(title="Minha busca de vagas", docs_url=None, redoc_url=None, openapi_url=None)
security = HTTPBasic()
CSS = """
:root{color-scheme:dark;font:16px system-ui,sans-serif;background:#0b1520;color:#e8f2fa}
*{box-sizing:border-box}body{margin:0}a{color:#78d8cd;text-decoration:none}a:hover{text-decoration:underline}
header{background:#122434;border-bottom:1px solid #2b4659;padding:22px max(24px,calc((100vw - 1100px)/2))}
header h1{margin:0;font-size:25px}header p{color:#a8bdca;margin:6px 0 0}
main{max-width:1100px;margin:28px auto;padding:0 24px}.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:22px}
input,select,textarea,button{font:inherit;border-radius:7px;padding:9px 12px;background:#142b3c;color:#f1f8fb;border:1px solid #36566a}
button{background:#0c897a;border:0;font-weight:700;cursor:pointer}button:hover{background:#0ba793}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px}
.card,.panel{background:#132535;border:1px solid #2a4354;border-radius:12px;padding:19px}
.card h2{font-size:19px;line-height:1.3;margin:8px 0}.muted{color:#a9bfca;font-size:14px}
.pill{display:inline-block;border-radius:30px;padding:4px 9px;background:#244a52;color:#b9fff1;font-size:12px;font-weight:700}
.pill.off{background:#483a39;color:#eac1b8}.row{display:flex;justify-content:space-between;gap:10px}
.links{display:flex;flex-wrap:wrap;gap:12px;margin-top:14px}.error{color:#ffb9ac}
pre{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.55;background:#0c1a26;padding:16px;border-radius:8px}
textarea{width:100%;min-height:80px}.panel{margin-bottom:18px}form.inline{display:inline}
"""


def person():
    return os.environ.get("PLATFORM_PERSON", "glaucojunior")


def guard(credentials: HTTPBasicCredentials = Depends(security)):
    username = os.environ.get("PLATFORM_USER", "")
    password = os.environ.get("PLATFORM_PASSWORD", "")
    valid = bool(username and password) and secrets.compare_digest(
        credentials.username.encode(), username.encode()) and secrets.compare_digest(
        credentials.password.encode(), password.encode())
    if not valid:
        raise HTTPException(401, "Autenticação necessária", headers={"WWW-Authenticate": "Basic"})
    return True


def token():
    password = os.environ.get("PLATFORM_PASSWORD", "")
    return hashlib.sha256((password + ":forms").encode()).hexdigest()


async def form(request):
    body = await request.body()
    if len(body) > 16384:
        raise HTTPException(413, "Formulário muito grande")
    data = parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
    if not secrets.compare_digest((data.get("csrf") or [""])[0], token()):
        raise HTTPException(403, "Token do formulário inválido")
    return {key: values[0] for key, values in data.items()}


def e(value):
    return html.escape(str(value or ""), quote=True)


def shell(title, body):
    return HTMLResponse(f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · Minha busca</title><style>{CSS}</style></head><body>
<header><h1><a href="/">Minha busca de vagas</a></h1>
<p>DevOps · SRE · Infraestrutura | Documentos locais, candidatura sob seu controle</p></header>
<main>{body}</main></body></html>""")


def get_row(identity):
    if not re.fullmatch(r"[0-9a-f]{20}", identity):
        raise HTTPException(404)
    _, output = paths(person())
    con = database(output)
    row = con.execute("SELECT * FROM jobs WHERE id=?", (identity,)).fetchone()
    con.close()
    if row is None:
        raise HTTPException(404)
    return row


@app.get("/", dependencies=[Depends(guard)])
def index(q: str = "", filter: str = "todas"):
    _, output = paths(person())
    con = database(output)
    rows = con.execute("SELECT * FROM jobs ORDER BY eligible DESC, score DESC, first_seen DESC LIMIT 800").fetchall()
    con.close()
    q = q.strip()[:80].casefold()
    rows = [r for r in rows if (not q or q in (r["title"] + " " + r["company"] + " " + r["location"]).casefold())
            and (filter == "todas" or (filter == "compatíveis" and r["eligible"]) or r["status"] == filter)]
    last = output / "last-run.json"
    summary = "Nenhuma coleta executada ainda."
    if last.exists():
        import json
        info = json.loads(last.read_text(encoding="utf-8"))
        summary = (f"Última coleta: {e(info['completed_at'])} · {info['collected']} recebidas · "
                   f"{info['new']} novas · {info['generated']} documentos gerados")
        if info.get("errors"):
            summary += f" · {len(info['errors'])} pendência(s); confira o log do comando run."
    cards = []
    for r in rows:
        mark = "Aderente" if r["eligible"] else "Revisar critérios"
        cls = "" if r["eligible"] else " off"
        doc = "PDF pronto" if r["generated_at"] else (r["generation_error"] or "Aguardando geração")
        cards.append(f"""<article class="card"><div class="row"><span class="pill{cls}">{mark}</span>
<span class="muted">{e(r['score'])} pontos</span></div>
<h2><a href="/jobs/{r['id']}">{e(r['title'])}</a></h2>
<p>{e(r['company'] or 'Empresa a confirmar')} · {e(r['location'] or 'Local a confirmar')}</p>
<p class="muted">{e(r['source'])} · {e(r['status'])}<br>{e(doc)}</p>
<div class="links"><a href="/jobs/{r['id']}">Ver detalhes</a>
<a href="{e(r['url'])}" target="_blank" rel="noopener noreferrer">Abrir vaga ↗</a></div></article>""")
    form_run = f'<form method="post" action="/run" class="inline"><input type="hidden" name="csrf" value="{token()}"><button type="submit">Buscar vagas agora</button></form>'
    toolbar = f"""<div class="toolbar">{form_run}
<form method="get" action="/"><input name="q" placeholder="Cargo, empresa ou local" value="{e(q)}">
<select name="filter"><option value="todas">Todas</option><option value="compatíveis">Aderentes</option>
<option value="avaliar">Para avaliar</option><option value="candidatada">Candidatadas</option>
<option value="descartada">Descartadas</option></select><button>Filtrar</button></form></div>"""
    return shell("Vagas", f'<p class="muted">{summary}</p>{toolbar}<p>{len(rows)} vaga(s) nesta visualização</p>'
                 f'<section class="grid">{"".join(cards) if cards else "<p>Nenhuma vaga encontrada neste filtro.</p>"}</section>')


@app.get("/jobs/{identity}", dependencies=[Depends(guard)])
def detail(identity: str):
    r = get_row(identity)
    _, output = paths(person())
    dest = output / "documents" / identity
    files = ""
    if (dest / "resume.pdf").exists():
        files += f'<a href="/jobs/{identity}/resume.pdf">Baixar currículo PDF</a>'
    if (dest / "interview.md").exists():
        files += f'<a href="/jobs/{identity}/interview.md">Baixar roteiro de entrevista</a>'
    if not files:
        files = "Documentos pendentes. Confira o perfil mestre e a última coleta."
    statuses = "".join(f'<option value="{e(s)}" {"selected" if r["status"] == s else ""}>{e(s.title())}</option>'
                       for s in ("nova", "avaliar", "candidatada", "descartada"))
    return shell(r["title"], f"""<p><a href="/">← Voltar</a></p><div class="panel">
<span class="pill">{e(r['source'])}</span><h1>{e(r['title'])}</h1>
<p>{e(r['company'])} · {e(r['location'])}</p>
<p><a href="{e(r['url'])}" target="_blank" rel="noopener noreferrer">Abrir vaga original ↗</a></p>
<p class="muted">Pontuação: {r['score']} · Requisitos encontrados: {e(r['reasons']) or 'insuficientes'}</p>
<div class="links">{files}</div><p class="error">{e(r['generation_error'])}</p>
<form method="post" action="/jobs/{identity}/generate">
<input type="hidden" name="csrf" value="{token()}"><button>Gerar documentos novamente</button></form></div>
<div class="panel"><h2>Acompanhar candidatura</h2>
<form method="post" action="/jobs/{identity}/status">
<input type="hidden" name="csrf" value="{token()}">
<label>Status <select name="status">{statuses}</select></label>
<p><label>Nota pessoal<br><textarea name="note" maxlength="2000">{e(r['note'])}</textarea></label></p>
<button>Salvar acompanhamento</button></form></div>
<div class="panel"><h2>Descrição recebida</h2><pre>{e(r['description'] or 'Abra o anúncio original para ver os requisitos completos.')}</pre></div>""")


@app.post("/run", dependencies=[Depends(guard)])
async def run_now(request: Request):
    await form(request)
    await run_in_threadpool(run, person())
    return RedirectResponse("/", status_code=303)


@app.post("/jobs/{identity}/generate", dependencies=[Depends(guard)])
async def regenerate(identity: str, request: Request):
    await form(request)
    private, output, _, policy = config(person())
    con = database(output)
    row = con.execute("SELECT * FROM jobs WHERE id=?", (identity,)).fetchone() if re.fullmatch(r"[0-9a-f]{20}", identity) else None
    if row is None:
        con.close()
        raise HTTPException(404)
    try:
        generate(con, row, person(), policy, output)
    except Exception as exc:
        con.execute("UPDATE jobs SET generation_error=? WHERE id=?", (str(exc)[:300], identity))
        con.commit()
    finally:
        con.close()
    return RedirectResponse(f"/jobs/{identity}", status_code=303)


@app.post("/jobs/{identity}/status", dependencies=[Depends(guard)])
async def status(identity: str, request: Request):
    data = await form(request)
    if not re.fullmatch(r"[0-9a-f]{20}", identity) or data.get("status") not in ALLOWED_STATUS:
        raise HTTPException(400)
    _, output = paths(person())
    con = database(output)
    con.execute("UPDATE jobs SET status=?, note=? WHERE id=?",
                (data["status"], data.get("note", "")[:2000], identity))
    con.commit()
    con.close()
    return RedirectResponse(f"/jobs/{identity}", status_code=303)


@app.get("/jobs/{identity}/{document}", dependencies=[Depends(guard)])
def download(identity: str, document: str):
    get_row(identity)
    if document not in {"resume.pdf", "interview.md"}:
        raise HTTPException(404)
    _, output = paths(person())
    file = output / "documents" / identity / document
    if not file.is_file():
        raise HTTPException(404)
    return FileResponse(file, filename=f"{identity}-{document}", media_type=(
        "application/pdf" if document.endswith(".pdf") else "text/markdown"))
