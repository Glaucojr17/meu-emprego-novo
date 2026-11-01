#!/usr/bin/env python3
"""Converte um resume.json em um arquivo .tex simples (uma coluna, ATS-friendly).

Uso: python3 scripts/json_para_latex.py entrada.json saida.tex
Compile depois com: pdflatex saida.tex
"""
import json
import re
import sys

ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def esc(texto):
    """Escapa caracteres especiais do LaTeX. Também converte **negrito** de markdown."""
    texto = str(texto)
    texto = "".join(ESCAPES.get(c, c) for c in texto)
    return re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", texto)


def periodo(item):
    ini, fim = item.get("startDate", ""), item.get("endDate", "")
    if fim == "Present":
        fim = "Atual"
    if ini and fim:
        return f"{ini} -- {fim}"
    return ini or fim


def secao(titulo):
    return f"\n\\section*{{{esc(titulo)}}}\n"


def gerar(d):
    b = d["basics"]
    loc = b.get("location", {})
    local = ", ".join(x for x in (loc.get("city"), loc.get("region")) if x)
    contatos = " $\\cdot$ ".join(esc(x) for x in (local, b.get("email"), b.get("phone"), b.get("url")) if x)

    out = [
        r"\documentclass[10pt,a4paper]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[margin=1.8cm]{geometry}",
        r"\usepackage{enumitem}",
        r"\usepackage{titlesec}",
        r"\setlist[itemize]{leftmargin=1.2em,itemsep=1pt,topsep=2pt}",
        r"\titleformat{\section}{\large\bfseries}{}{0em}{}[\titlerule]",
        r"\titlespacing*{\section}{0pt}{10pt}{4pt}",
        r"\pagestyle{empty}",
        r"\setlength{\parindent}{0pt}",
        r"\begin{document}",
        f"{{\\LARGE\\bfseries {esc(b['name'])}}}\\\\[2pt]",
        f"{{\\large {esc(b.get('label', ''))}}}\\\\[2pt]",
        contatos,
        secao("Resumo"),
        esc(b.get("summary", "")),
        secao("Experiência"),
    ]

    for w in d["work"]:
        cab = f"\\textbf{{{esc(w['position'])}}}, {esc(w['name'])}"
        if w.get("location"):
            cab += f" ({esc(w['location'])})"
        out.append(f"{cab} \\hfill {esc(periodo(w))}\\\\")
        out.append(r"\begin{itemize}")
        out.extend(f"  \\item {esc(h)}" for h in w.get("highlights", []))
        out.append(r"\end{itemize}")

    if d.get("projects"):
        out.append(secao("Projetos"))
        for p in d["projects"]:
            out.append(f"\\textbf{{{esc(p.get('name', ''))}}}: {esc(p.get('description', ''))}")
            if p.get("highlights"):
                out.append(r"\begin{itemize}")
                out.extend(f"  \\item {esc(h)}" for h in p["highlights"])
                out.append(r"\end{itemize}")

    out.append(secao("Competências"))
    for s in d["skills"]:
        out.append(f"\\textbf{{{esc(s['name'])}}}: {esc(', '.join(s.get('keywords', [])))}\\\\")

    out.append(secao("Formação"))
    for e in d["education"]:
        linha = f"\\textbf{{{esc(e.get('studyType', ''))} em {esc(e.get('area', ''))}}}, {esc(e.get('institution', ''))}"
        out.append(f"{linha} \\hfill {esc(periodo(e))}\\\\")

    if d.get("certificates"):
        out.append(secao("Certificações"))
        out.append(r"\begin{itemize}")
        for c in d["certificates"]:
            extra = " ".join(x for x in (c.get("issuer"), c.get("date")) if x)
            out.append(f"  \\item {esc(c['name'])}" + (f" ({esc(extra)})" if extra else ""))
        out.append(r"\end{itemize}")

    if d.get("languages"):
        out.append(secao("Idiomas"))
        out.append(esc(", ".join(f"{l['language']} ({l['fluency']})" for l in d["languages"])))

    out.append(r"\end{document}")
    return "\n".join(out) + "\n"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        dados = json.load(f)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(gerar(dados))
    print(f"gerado: {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
