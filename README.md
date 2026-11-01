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

## Contribuindo e licença

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Nunca inclua dados pessoais reais em issues ou PRs. Licença MIT, baseada no projeto original de Rushi Chaudhari
([0xrushi](https://github.com/0xrushi)); veja [LICENSE](LICENSE).
