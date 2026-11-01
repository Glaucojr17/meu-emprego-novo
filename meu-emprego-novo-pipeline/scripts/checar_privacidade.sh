#!/usr/bin/env bash
# Procura sinais de dados pessoais nos arquivos versionáveis do repositório.
# Uso: bash scripts/checar_privacidade.sh
# Saída: código 0 se nada suspeito; 1 se achar algo.

set -u
raiz="$(cd "$(dirname "$0")/.." && pwd)"
cd "$raiz" || exit 2

# Arquivos candidatos ao commit, ignorando privado/ e .git/
arquivos=$(find . -type f \
  -not -path "./.git/*" -not -path "./privado/*" \
  -not -name "*.pdf" -not -name "checar_privacidade.sh" \
  \( -name "*.md" -o -name "*.json" -o -name "*.tex" -o -name "*.csv" -o -name "*.py" -o -name "*.txt" \))

achou=0

verificar() {
  local rotulo="$1" padrao="$2" excecao="${3:-}"
  local resultado
  resultado=$(echo "$arquivos" | xargs grep -nEH "$padrao" 2>/dev/null)
  if [ -n "$excecao" ]; then
    resultado=$(echo "$resultado" | grep -vE "$excecao")
  fi
  if [ -n "$resultado" ]; then
    echo "== Suspeita: $rotulo =="
    echo "$resultado"
    echo
    achou=1
  fi
}

# E-mails que não sejam de exemplo
verificar "e-mail real" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' '@exemplo\.com|@example\.com|seu\.email@'
# Telefones brasileiros
verificar "telefone" '\(?[0-9]{2}\)?[ -]?9?[0-9]{4}-?[0-9]{4}'
# CPF
verificar "CPF" '[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}'
# Perfis de LinkedIn que não sejam placeholder
verificar "perfil LinkedIn" 'linkedin\.com/in/[A-Za-z0-9_-]+' 'seu-perfil|ana-souza-exemplo'

if [ "$achou" -eq 0 ]; then
  echo "OK: nenhum dado pessoal óbvio encontrado."
  echo "Mesmo assim, releia os arquivos antes de publicar."
  exit 0
fi

echo "Revise os itens acima antes de fazer commit."
exit 1
