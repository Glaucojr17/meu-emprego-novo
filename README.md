# Agente da Meia Idade (*Mid-Life Agent*)

![logo](images/logo.jpeg)

Uma equipe de agentes de IA que reposiciona o seu currículo para cada vaga.

> **Feita por um dev, para devs.** Não é um SaaS polido: é uma ferramenta que um desenvolvedor
> escreveu para resolver o próprio problema. Por isso é uma CLI, é hackeável, e cada prompt, agente
> e template é código simples que você pode ler e alterar. Foi criada por um profissional de TI com
> 30+ anos de carreira para voltar ao mercado, e funcionou: **5 meses depois, ele foi contratado.**
> Agora é código aberto para ajudar você também.

Os agentes *Estrategista de Carreira*, *Gerente de Contratação*, *Editor de Currículo* e *Candidato*
(sobre o [CrewAI](https://docs.crewai.com)) iteram até o currículo atingir nota ≥ 8.5 para a vaga.

![antes/depois](images/before_after.png)

## Destaques

- **Sem histórias falsas.** A IA só seleciona e reescreve o que está nas suas fontes; o `profile_truth.md` tem prioridade sobre tudo.
- **Um currículo por vaga:** cole a descrição da vaga e receba JSON + LaTeX + PDF sob medida.
- **Multi-LLM:** OpenAI, Anthropic, Gemini, Grok (xAI) ou AWS Bedrock.
- **Multi-pessoa:** dados isolados por pessoa (`input/`, `data/`, `outputs/`).
- **Saída bilíngue:** `--lang pt-BR` (padrão) ou `--lang en`.
- **Cobertura completa da carreira:** todas as posições são mantidas, da mais recente à mais antiga; sem limite fixo de bullets ou páginas.
- **Pipeline completo de busca de emprego:** da triagem de vagas à preparação de entrevista e ao rastreamento, em [meu-emprego-novo-pipeline](#pipeline-de-busca-de-emprego-meu-emprego-novo-pipeline).

## ⚠️ Privacidade em primeiro lugar

Seu currículo é dado pessoal. Durante a geração, os arquivos são **enviados ao provedor de IA configurado**.

- `input/`, `data/` e `outputs/` estão no `.gitignore` de propósito. **Nunca os versione nem publique os resultados.**
- Chaves de API só no `.env` (ignorado pelo git). No Bedrock, use um perfil do AWS CLI.
- Não escreva no `profile_truth.md` nada que você não queira enviar ao provedor.

## Como funciona

```
input/<voce>/  currículos PDF/DOCX + profile_truth.md (+ about_me.md)
      │  ingest_resume.py
      ▼
data/<voce>/resume.json   ← fonte canônica (nunca sobrescrita)
      │  + descrição da vaga
      ▼
agentes (estrategista → gerente de contratação → editor → candidato) ─ iteram até nota ≥ 8.5
      ▼
outputs/<voce>/<cargo>/{json,latex,pdf}
```

## Início rápido

Requisitos: Python 3.12, uma distribuição LaTeX (para o PDF) e uma chave de API de um provedor.

```bash
git clone https://github.com/R238Company/meu-emprego-novo.git && cd meu-emprego-novo
pip install -r requirements.txt
cp .env.example .env            # defina LLM_PROVIDER e sua chave

# Teste com o exemplo fictício: "Dev Procurando", dev Full-Stack (React + Node + Supabase + Vercel)
mkdir -p input/dev_procurando data/dev_procurando/job_profiles
cp examples/dev_procurando/profile_truth.md examples/dev_procurando/job_desc.md input/dev_procurando/
cp examples/dev_procurando/resume.json data/dev_procurando/
cp examples/dev_procurando/job_profiles/*.txt data/dev_procurando/job_profiles/

python main.py --person dev_procurando --job --lang en
```

Um resultado pronto do exemplo está em [examples/dev_procurando/resume.pdf](examples/dev_procurando/resume.pdf).

## Como usar (passo a passo)

1. **Instale e configure.** Rode o Início rápido acima. No `.env`, defina `LLM_PROVIDER`
   (`openai`, `anthropic`, `gemini`, `grok` ou `bedrock`) e a chave correspondente.
2. **Crie sua pasta.** `mkdir input/<voce>`, onde `<voce>` é qualquer identificador (ex.: `maria_dev`).
   Coloque lá seus currículos atuais (PDF/DOCX).
3. **Escreva seu `profile_truth.md`.** Copie [examples/dev_procurando/profile_truth.md](examples/dev_procurando/profile_truth.md)
   para `input/<voce>/` e preencha. Ele é o seu guardrail: o que está lá vale mais que qualquer PDF,
   e o que estiver em "DO NOT INCLUDE" nunca chega ao currículo.
   Dica: peça para uma IA entrevistar você e salve a transcrição em `input/<voce>/about_me.md`.
4. **Gere o JSON base.** `python -m src.scripts.ingest_resume --person <voce>` cria
   `data/<voce>/resume.json`, a fonte canônica que nunca é sobrescrita. Revise e corrija o que estiver errado.
5. **Adicione a vaga.** Cole a descrição em `input/<voce>/job_desc.md`.
6. **Rode.** `python main.py --person <voce> --job` (use `--lang en` para inglês).
   Os agentes iteram até o currículo atingir nota ≥ 8.5 para a vaga.
7. **Pegue o resultado** em `outputs/<voce>/<cargo>/` (`json/`, `latex/`, `pdf/`).
   Leia sempre antes de enviar: você é responsável pelo que sai com o seu nome.

Reaproveite a mesma base para várias vagas: salve um perfil curto em `data/<voce>/job_profiles/<nome>.txt`
e rode `--role <nome>`, ou gere todos com `--all`.

Outros comandos: `--provider`, `--list-roles`, `--list-people`,
`python src/scripts/run_compare_pdf.py` (diff estilo GitHub contra o original).

## AWS Bedrock

```dotenv
LLM_PROVIDER=bedrock
AWS_PROFILE=mid-life-agent
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-opus-4-6-v1
BEDROCK_FALLBACK_MODEL_ID=us.anthropic.claude-sonnet-4-6   # vazio desativa o fallback
BEDROCK_EXTRACTION_MODEL_ID=deepseek.v3.2
BEDROCK_MAX_TOKENS=16384
```

Crie um perfil restrito no AWS CLI e adapte [infra/aws/bedrock-policy.json](infra/aws/bedrock-policy.json)
(troque `123456789012` pelo ID da sua conta). As tentativas extras e o único fallback para o Sonnet valem
apenas para throttling/indisponibilidade; erros de permissão e validação são propagados.
Testes offline: `python -m unittest discover -s tests -v`.

## Pipeline de busca de emprego (`meu-emprego-novo-pipeline/`)

O gerador de currículos é só uma etapa de um processo maior. A pasta [meu-emprego-novo-pipeline](meu-emprego-novo-pipeline/README.md)
traz o passo a passo reproduzível de como a busca foi organizada com ajuda de IA, e terminou em contratação:
perfil-mestre, vagas triadas, currículo sob medida, revisão de cobertura, preparação para entrevista e acompanhamento das candidaturas.

```
perfil-mestre → busca → triagem → currículo sob medida → revisão de cobertura
                                                      → preparação de entrevista
                                                      → rastreamento → aprendizado
```

> **Ensina o método, não expõe a vida de ninguém.** Todos os exemplos usam uma persona fictícia (Ana Souza).
> Não serve para fabricar experiência, burlar triagem ou se candidatar em massa sem ler as vagas.

| # | Etapa | Saída | Documento |
|---|-------|-------|-----------|
| 0 | Princípios | regras de jogo | [00-principios](meu-emprego-novo-pipeline/docs/00-principios.md) |
| 1 | Perfil-mestre | `profile_truth.md` | [01-profile-truth](meu-emprego-novo-pipeline/docs/01-profile-truth.md) |
| 2 | Busca de vagas | lista numerada de vagas | [02-busca-de-vagas](meu-emprego-novo-pipeline/docs/02-busca-de-vagas.md) |
| 3 | Triagem | vagas por aderência | [03-triagem](meu-emprego-novo-pipeline/docs/03-triagem.md) |
| 4 | Currículo sob medida | `resume.json` → `.tex` → PDF | [04-curriculo-sob-medida](meu-emprego-novo-pipeline/docs/04-curriculo-sob-medida.md) |
| 5 | Revisão de cobertura | `coverage_review.md` | [05-coverage-review](meu-emprego-novo-pipeline/docs/05-coverage-review.md) |
| 6 | Preparação de entrevista | `interview_prep.md` | [06-interview-prep](meu-emprego-novo-pipeline/docs/06-interview-prep.md) |
| 7 | Rastreamento | `tracker.csv` | [07-rastreamento](meu-emprego-novo-pipeline/docs/07-rastreamento.md) |
| 8 | Golpes e segurança | checklist | [08-golpes-e-seguranca](meu-emprego-novo-pipeline/docs/08-golpes-e-seguranca.md) |
| 9 | LinkedIn | plano de otimização | [09-linkedin](meu-emprego-novo-pipeline/docs/09-linkedin.md) |
| 10 | Resultados e lições | retrospectiva | [10-resultados-e-licoes](meu-emprego-novo-pipeline/docs/10-resultados-e-licoes.md) |

Teste o pipeline com a persona de exemplo (Python 3.9+, só biblioteca padrão):

```bash
cd meu-emprego-novo-pipeline
python3 scripts/validar_json.py exemplo/resume.json
python3 scripts/json_para_latex.py exemplo/resume.json exemplo/curriculo.tex
bash scripts/checar_privacidade.sh   # rode antes de cada commit
```

### Regras de ouro

1. **Uma única fonte de verdade.** Todo currículo deriva do `profile_truth.md`; fato que não está lá não vai para o currículo.
2. **Nunca invente métricas.** A revisão de cobertura existe para pegar números divergentes.
3. **A IA propõe, você decide.** Leia tudo o que for enviado em seu nome.
4. **Lacuna declarada vale mais que maquiagem.**
5. **Exclusões são regra, não sugestão.**
6. **Segredos ficam fora do chat.** Senhas, documentos e dados bancários não entram em prompts.
7. **Versione o método, não os dados.** O que é seu fica em `privado/`, nunca versionada.

### Segurança: golpes de recrutamento

- Entrevista que pede para baixar e rodar código (inclusive um repositório "para achar um bug"): recuse.
- Formulário que pede documento de identidade na candidatura: deixe em branco; documento só na contratação, por canal oficial.
- Pedido de pagamento, taxa ou "kit": golpe.
- Domínio de e-mail diferente do da empresa, urgência exagerada, proposta boa demais: confirme pelo site oficial.

Versão completa, instalação detalhada, FAQ e prompts de cada etapa em [meu-emprego-novo-pipeline/README.md](meu-emprego-novo-pipeline/README.md).

## Contribuindo e licença

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Nunca inclua dados pessoais reais em issues ou PRs. Licença MIT, baseada no projeto original de Rushi Chaudhari
([0xrushi](https://github.com/0xrushi)); veja [LICENSE](LICENSE).
