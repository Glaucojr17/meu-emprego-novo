# meu-emprego-novo-pipeline

Um passo a passo reproduzível de como montei, com ajuda de IA, um processo organizado de busca de emprego: currículo-mestre, vagas triadas, currículo sob medida por vaga, revisão de cobertura, preparação para entrevista e acompanhamento das candidaturas. O processo terminou em contratação.

> **Este repositório ensina o método, não expõe a minha vida.** Todos os exemplos usam uma persona fictícia (Ana Souza). Nenhum currículo, contato, recrutador ou empresa real está aqui.

---

## Sumário

1. [O que é e para quem serve](#1-o-que-é-e-para-quem-serve)
2. [Visão geral do fluxo](#2-visão-geral-do-fluxo)
3. [Pré-requisitos](#3-pré-requisitos)
4. [Instalação passo a passo](#4-instalação-passo-a-passo)
5. [Guia de uso: do zero à candidatura](#5-guia-de-uso-do-zero-à-candidatura)
6. [Estrutura do repositório](#6-estrutura-do-repositório)
7. [Regras de ouro](#7-regras-de-ouro)
8. [Privacidade: o que nunca versionar](#8-privacidade-o-que-nunca-versionar)
9. [Segurança: golpes de recrutamento](#9-segurança-golpes-de-recrutamento)
10. [Perguntas frequentes](#10-perguntas-frequentes)
11. [Como contribuir](#11-como-contribuir)
12. [Licença](#12-licença)

---

## 1. O que é e para quem serve

Procurar emprego vira um trabalho de volume: dezenas de vagas, cada uma pedindo um currículo ligeiramente diferente, entrevistas com perguntas previsíveis, mensagens de recrutadores para acompanhar. Este projeto trata isso como um **pipeline de dados**:

```
perfil-mestre → busca → triagem → currículo sob medida → revisão de cobertura
                                                      → preparação de entrevista
                                                      → rastreamento → aprendizado
```

Serve para quem:
- tem experiência real e quer apresentá-la de forma diferente para vagas diferentes, sem inventar nada;
- usa (ou quer usar) um assistente de IA como ferramenta de trabalho, mas quer manter o controle;
- quer um processo, não uma pilha de PDFs soltos.

Não serve para fabricar experiência, burlar triagem ou candidatar-se em massa sem ler as vagas.

## 2. Visão geral do fluxo

| # | Etapa | Entrada | Saída | Documento |
|---|-------|---------|-------|-----------|
| 0 | Princípios | — | regras de jogo | [docs/00-principios.md](docs/00-principios.md) |
| 1 | Perfil-mestre | sua história real | `profile_truth.md` | [docs/01-profile-truth.md](docs/01-profile-truth.md) |
| 2 | Busca de vagas | perfil + preferências | lista numerada de vagas | [docs/02-busca-de-vagas.md](docs/02-busca-de-vagas.md) |
| 3 | Triagem | lista de vagas | vagas classificadas por aderência | [docs/03-triagem.md](docs/03-triagem.md) |
| 4 | Currículo sob medida | perfil + vaga | `resume.json` → `.tex` → PDF | [docs/04-curriculo-sob-medida.md](docs/04-curriculo-sob-medida.md) |
| 5 | Revisão de cobertura | vaga + currículo | `coverage_review.md` | [docs/05-coverage-review.md](docs/05-coverage-review.md) |
| 6 | Preparação de entrevista | vaga + currículo | `interview_prep.md` | [docs/06-interview-prep.md](docs/06-interview-prep.md) |
| 7 | Rastreamento | candidaturas, respostas | `tracker.csv` | [docs/07-rastreamento.md](docs/07-rastreamento.md) |
| 8 | Golpes e segurança | situações suspeitas | checklist | [docs/08-golpes-e-seguranca.md](docs/08-golpes-e-seguranca.md) |
| 9 | LinkedIn | perfil-mestre | plano de otimização | [docs/09-linkedin.md](docs/09-linkedin.md) |
| 10 | Resultados e lições | tudo acima | retrospectiva | [docs/10-resultados-e-licoes.md](docs/10-resultados-e-licoes.md) |

## 3. Pré-requisitos

**Obrigatórios**
- Python 3.9 ou superior (os scripts usam só a biblioteca padrão).
- Git.
- Um assistente de IA com contexto persistente. No meu caso foi o Claude com um *Projeto* (onde ficam os arquivos-base) e memória. Funciona com qualquer assistente que permita anexar arquivos e reaproveitar instruções.

**Para gerar PDF**
- Uma distribuição LaTeX com `pdflatex` (TeX Live, MiKTeX) ou o `tectonic`.

**Opcionais (aceleram a busca)**
- Conectores/ferramentas do assistente para sites de vagas, quando existirem.
- Navegador automatizado para páginas que exigem login. Faça o login você mesmo; nunca entregue senhas ao assistente.

## 4. Instalação passo a passo

```bash
# 1. Clonar
git clone https://github.com/SEU-USUARIO/meu-emprego-novo-pipeline.git
cd meu-emprego-novo-pipeline

# 2. Criar a sua área privada (já está no .gitignore, nada daqui sobe para o GitHub)
mkdir -p privado/perfil privado/vagas privado/curriculos privado/entrevistas
cp templates/profile_truth.md privado/perfil/profile_truth.md
cp templates/vagas_excluidas.md privado/vagas/vagas_excluidas.md
cp templates/tracker.csv privado/tracker.csv

# 3. Testar o pipeline com a persona de exemplo
python3 scripts/validar_json.py exemplo/resume.json
python3 scripts/json_para_latex.py exemplo/resume.json exemplo/curriculo.tex
pdflatex -output-directory exemplo exemplo/curriculo.tex   # opcional
```

Se os três comandos de teste funcionarem, o ambiente está pronto. O passo 2 é importante: **tudo que for seu fica em `privado/`**, e a pasta nunca é versionada.

Antes de cada commit, rode:

```bash
bash scripts/checar_privacidade.sh
```

O script procura e-mails, telefones e padrões de documento fora de `exemplo/` e `templates/`, e avisa se achar algo.

## 5. Guia de uso: do zero à candidatura

### Passo 1: construir o perfil-mestre (1 a 2 horas, uma vez só)

1. Abra `privado/perfil/profile_truth.md` e preencha cada empregador, cargo, período, o que você **realmente** fez, tecnologias e resultados que você consegue comprovar.
2. Marque cada número com a origem (`[medido]`, `[estimado]`, `[sem número]`). Métrica que você não consegue defender numa entrevista não entra.
3. Registre também as lacunas: o que você **não** fez ou só estudou. Esse arquivo é a fonte de verdade de tudo o que vem depois.
4. Anexe o arquivo ao seu projeto no assistente e instrua: *"profile_truth.md é a única fonte de fatos; nunca afirme nada que não esteja nele."*

Detalhes em [docs/01-profile-truth.md](docs/01-profile-truth.md).

### Passo 2: definir preferências e exclusões

Preencha `privado/vagas/vagas_excluidas.md` com empresas e tipos de vaga que você não quer, e **o motivo apenas para você**. Peça ao assistente que consulte esse arquivo antes de qualquer busca ou candidatura. Veja [docs/02-busca-de-vagas.md](docs/02-busca-de-vagas.md).

### Passo 3: buscar vagas

Use o prompt de [prompts/02-busca-vagas.md](prompts/02-busca-vagas.md). Peça resultados **numerados** e separados por tipo de candidatura (simplificada na própria plataforma × externa no site da empresa), sempre com link, data e requisitos principais. A numeração permite dizer depois "candidate-se à 3 e à 7".

### Passo 4: triar

Use [prompts/03-triagem.md](prompts/03-triagem.md). O assistente classifica cada vaga em **alta**, **média** ou **baixa** aderência e justifica com base no `profile_truth.md`. Você decide; a IA só organiza. Descarte sem culpa o que for golpe, presencial fora da sua cidade, ou empresa da lista de exclusão.

### Passo 5: gerar o currículo sob medida

1. Crie uma pasta `privado/curriculos/<nome-da-vaga>/`.
2. Cole a descrição da vaga em `vaga.md`.
3. Use [prompts/04-curriculo-sob-medida.md](prompts/04-curriculo-sob-medida.md) para o assistente produzir `resume.json` a partir do `profile_truth.md` e da vaga.
4. Valide e gere o PDF:

```bash
python3 scripts/validar_json.py privado/curriculos/<vaga>/resume.json
python3 scripts/json_para_latex.py privado/curriculos/<vaga>/resume.json privado/curriculos/<vaga>/curriculo.tex
pdflatex -output-directory privado/curriculos/<vaga> privado/curriculos/<vaga>/curriculo.tex
```

5. Abra o PDF e **leia inteiro**. Confira datas, cargos, números e se coube no número de páginas que você quer.

### Passo 6: revisar a cobertura

Use [prompts/05-coverage-review.md](prompts/05-coverage-review.md). O assistente compara os requisitos da vaga com o currículo e produz `coverage_review.md` com três listas: **cobertos com evidência**, **cobertos parcialmente** e **lacunas que não serão inventadas**. Se uma lacuna é obrigatória, decida com honestidade se vale candidatar-se.

### Passo 7: preparar a entrevista

Use [prompts/06-interview-prep.md](prompts/06-interview-prep.md). Gere perguntas prováveis, respostas no formato STAR baseadas **só em fatos do perfil-mestre**, pontos fracos a antecipar e perguntas para fazer ao entrevistador. Depois **reescreva as respostas com suas palavras**: texto gerado não é fala natural.

### Passo 8: candidatar-se e registrar

1. Aplique você mesmo, lendo cada formulário.
2. Nunca preencha número de documento de identidade em formulário de vaga (veja [docs/08-golpes-e-seguranca.md](docs/08-golpes-e-seguranca.md)).
3. Registre em `privado/tracker.csv`: data, empresa, vaga, link, versão do currículo, status.
4. Quando alguém responder, atualize o status e o que foi combinado.

### Passo 9: aprender e iterar

A cada semana, olhe o tracker: quais versões de currículo geram resposta? Quais fontes de vaga rendem? Onde você desistiu e por quê? Ajuste o perfil-mestre e os prompts. Veja [docs/10-resultados-e-licoes.md](docs/10-resultados-e-licoes.md).

## 6. Estrutura do repositório

```
meu-emprego-novo-pipeline/
├── README.md
├── LICENSE
├── .gitignore               # ignora privado/ e arquivos pessoais
├── docs/                    # o tutorial, capítulo por capítulo (00 a 10)
├── prompts/                 # os prompts de cada etapa, prontos para adaptar
├── templates/               # arquivos em branco para começar
│   ├── profile_truth.md
│   ├── resume.json
│   ├── vagas_excluidas.md
│   └── tracker.csv
├── scripts/
│   ├── validar_json.py          # confere campos obrigatórios do resume.json
│   ├── json_para_latex.py       # converte resume.json em .tex
│   └── checar_privacidade.sh    # procura dados pessoais antes do commit
├── exemplo/                 # persona fictícia com o fluxo completo
└── privado/                 # SUA área (criada por você, nunca versionada)
```

## 7. Regras de ouro

1. **Uma única fonte de verdade.** Todo currículo deriva do `profile_truth.md`. Se um fato não está lá, não vai para o currículo.
2. **Nunca invente métricas.** Na minha experiência, versões antigas de currículo e de preparação de entrevista acabaram com números divergentes para o mesmo projeto. A revisão de cobertura existe para pegar isso.
3. **A IA propõe, você decide.** Leia tudo o que for enviado em seu nome.
4. **Lacuna declarada vale mais que maquiagem.** Se não tem a habilidade, diga que está aprendendo, ou não se candidate.
5. **Exclusões são regra, não sugestão.** O que está em `vagas_excluidas.md` nunca volta.
6. **Segredos ficam fora do chat.** Senhas, documentos e dados bancários não entram em prompts.
7. **Versione o método, não os dados.** O que é seu fica em `privado/`.

## 8. Privacidade: o que nunca versionar

Mesmo com `.gitignore`, confira antes de publicar. Nunca suba:

- currículos reais (JSON, TeX, PDF) e o `profile_truth.md` real;
- telefone, e-mail pessoal, endereço, links de perfil pessoais;
- nomes de recrutadores, e-mails e mensagens recebidas;
- pretensão salarial, ofertas e valores combinados;
- planilhas de contatos;
- opiniões sobre empresas identificáveis;
- números de documentos de identificação ou de cartões.

Se algo sensível já foi commitado, **não adianta apagar no commit seguinte**: o histórico guarda tudo. Recrie o repositório do zero ou reescreva o histórico antes de publicar.

## 9. Segurança: golpes de recrutamento

Resumo (versão completa em [docs/08-golpes-e-seguranca.md](docs/08-golpes-e-seguranca.md)):

- **Entrevista que pede para baixar e rodar código**, inclusive um repositório "para achar um bug": recuse. Teste técnico legítimo acontece em plataforma conhecida, no navegador.
- **Formulário que pede documento de identidade na candidatura**: deixe em branco e pergunte para que serve. Documento só na contratação, por canal oficial.
- **Pedido de pagamento, taxa ou "kit"**: golpe.
- **Domínio de e-mail diferente do da empresa**, urgência exagerada, proposta boa demais: desconfie e confirme pelo site oficial.

## 10. Perguntas frequentes

**Preciso usar o mesmo assistente que você?** Não. O método só exige que o assistente leia seus arquivos-base e siga instruções estáveis.

**Posso usar com outra profissão?** Sim. Troque a persona e os exemplos; as etapas são as mesmas.

**Quantas versões de currículo devo ter?** Uma por família de vagas (por exemplo, "arquiteto" e "engenheiro de dados"), não uma por vaga. Ajuste só o necessário por candidatura.

**A IA vai deixar meu currículo com cara de robô?** Pode. Reescreva o resumo e os destaques com a sua voz.

**Posso confiar nas vagas que o assistente encontra?** Confira link, empresa e data. Resultados de busca podem estar desatualizados ou ser golpes.

## 11. Como contribuir

Issues e pull requests são bem-vindos, em especial:
- adaptações para outras áreas profissionais;
- novos templates de currículo;
- melhorias nos scripts;
- relatos de golpes (sem nomes e links reais).

Ao contribuir, não inclua dados pessoais seus nem de terceiros.

## 12. Licença

MIT. Veja [LICENSE](LICENSE). Use, adapte e compartilhe, e se este material ajudar você a conseguir uma vaga, conte a sua história em uma issue.
