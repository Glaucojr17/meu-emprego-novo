#!/usr/bin/env python3
"""Valida a estrutura básica de um resume.json.

Uso: python3 scripts/validar_json.py caminho/resume.json
Saída: código 0 se válido; 1 se houver erros.
"""
import json
import re
import sys

OBRIGATORIOS = ["basics", "work", "education", "skills"]
BASICS_OBRIGATORIOS = ["name", "label", "email", "summary"]
WORK_OBRIGATORIOS = ["name", "position", "startDate", "highlights"]
DATA_RE = re.compile(r"^(\d{4}(-\d{2})?|Present|Atual)$")


def validar(dados):
    erros, avisos = [], []

    for chave in OBRIGATORIOS:
        if chave not in dados:
            erros.append(f"campo obrigatório ausente: {chave}")
    if erros:
        return erros, avisos

    for campo in BASICS_OBRIGATORIOS:
        if not str(dados["basics"].get(campo, "")).strip():
            erros.append(f"basics.{campo} vazio")

    if not dados["work"]:
        erros.append("work está vazio")

    for i, emprego in enumerate(dados["work"]):
        rotulo = f"work[{i}] ({emprego.get('name', '?')})"
        for campo in WORK_OBRIGATORIOS:
            if campo not in emprego or emprego[campo] in ("", []):
                erros.append(f"{rotulo}: campo '{campo}' ausente ou vazio")
        for campo in ("startDate", "endDate"):
            valor = emprego.get(campo)
            if valor and not DATA_RE.match(str(valor)):
                erros.append(f"{rotulo}: {campo}='{valor}' fora do formato AAAA, AAAA-MM ou Present")
        if len(emprego.get("highlights", [])) > 8:
            avisos.append(f"{rotulo}: mais de 8 destaques; considere enxugar")

    for i, cert in enumerate(dados.get("certificates", [])):
        if not cert.get("name"):
            erros.append(f"certificates[{i}] sem nome")

    resumo = dados["basics"].get("summary", "")
    if len(resumo) > 700:
        avisos.append("basics.summary passa de 700 caracteres; resumo curto lê melhor")

    return erros, avisos


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            dados = json.load(f)
    except OSError as exc:
        print(f"ERRO ao ler o arquivo: {exc}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERRO: o arquivo não é um JSON válido ({exc}).")
        print("Salve só o JSON da resposta do assistente: do primeiro { ao último }, sem ``` e sem comentários.")
        return 1

    erros, avisos = validar(dados)
    for a in avisos:
        print(f"AVISO: {a}")
    for e in erros:
        print(f"ERRO: {e}")
    if erros:
        return 1
    print("OK: resume.json válido")
    return 0


if __name__ == "__main__":
    sys.exit(main())
