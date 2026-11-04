# Triagem pessoal de vagas e acompanhamento de candidaturas

Este módulo complementa a geração de currículo e roteiro de entrevista do projeto. Ele lê **seus próprios alertas de vaga** salvos como `.eml` e uma lista CSV de links diretos de LinkedIn ou Gupy. Cruza títulos, tecnologias e regime remoto com suas preferências, elimina duplicatas e prepara uma fila de revisão. A pontuação é uma triagem simples, não uma avaliação de recrutador ou garantia de elegibilidade.

## Limites e dados pessoais

- O módulo **não faz login, raspagem ou inscrição automática** no LinkedIn ou na Gupy. Essas plataformas têm regras de uso e fluxos diferentes de candidatura; algumas exigem perguntas, consentimento, testes e confirmação humana.
- O status `candidatada` exige que você já tenha concluído o envio e salvo um comprovante local. Vaga encontrada ou currículo preparado não conta como candidatura.
- Alertas, comprovantes, currículo e relatórios ficam em `input/`, `data/` e `outputs/`, ignorados pelo Git. Antes de publicar qualquer material, rode `git status --short` e confira se não contém dados pessoais.
- O pipeline original de currículo usa um provedor de IA configurado no `.env`: leia as políticas de privacidade desse provedor antes de enviar seu currículo. Esta triagem local usa apenas a biblioteca padrão do Python e não faz chamadas de rede.
- Texto de anúncios e alertas é informação externa. Revise a empresa, o link, os requisitos e o regime antes de seguir qualquer instrução do anúncio. Não execute comandos recebidos por e-mail.

## Configuração

Na raiz do repositório, com Python 3.9 ou superior:

```bash
mkdir -p input/glaucojunior/job_alerts
cp examples/opportunities/job_policy.example.json input/glaucojunior/job_policy.json
cp examples/opportunities/vagas.example.csv input/glaucojunior/vagas.csv
```

Edite a política para incluir seus títulos, habilidades e termos de exclusão. O exemplo contém tecnologias relevantes para DevOps, SRE e infraestrutura, mas não afirma que você domina todas elas. Se deseja apenas remoto, mantenha `remote_only: true`. Uma vaga sem menção explícita ao regime ficará pendente de comprovação.

Configure os alertas de vagas no próprio LinkedIn e na Gupy. Salve notificações recebidas em `input/glaucojunior/job_alerts/` como arquivos `.eml`. Se o e-mail trouxer apenas link de rastreamento, abra a vaga manualmente e registre o link direto e a descrição em `vagas.csv`. O CSV aceita `source,url,title,company,location,description`. Não coloque senhas ou cookies nesses arquivos.

## Rodar e revisar

```bash
python3 -m src.opportunities --person glaucojunior scan
```

Leia `outputs/glaucojunior/opportunities/relatorio.md` e `vagas.csv`. O relatório informa a aderência observada e distingue vagas encontradas de candidaturas efetivamente registradas. Links de alerta com informações incompletas podem receber pontuação baixa. Para cada vaga interessante, copie a descrição real para `input/glaucojunior/job_desc.md` e rode o projeto original:

```bash
python3 main.py --person glaucojunior --job input/glaucojunior/job_desc.md
```

O fluxo original gera o currículo adaptado e `interview_prep.md` na pasta da vaga sob `outputs/glaucojunior/`. Revise fatos, datas, técnicas e exemplos antes de usar. **Não invente experiências** para coincidir com a descrição.

Depois de concluir a candidatura no site e salvar o recibo ou captura de tela em `input/glaucojunior/`, registre:

```bash
python3 -m src.opportunities --person glaucojunior record \
  --url https://empresa-exemplo.gupy.io/jobs/123456 \
  --title 'Analista DevOps' \
  --evidence input/glaucojunior/comprovante-123456.png
python3 -m src.opportunities --person glaucojunior scan
```

O histórico fica em `outputs/glaucojunior/opportunities/historico.json`. Copie `input/` e `outputs/` para sua rotina privada de backup, sem incluí-los no repositório público. Nenhum comprovante é validado pela plataforma: o registro expressa sua confirmação de envio.

## Próxima evolução possível

Pode-se conectar uma fonte de vagas autorizada ou notificações por e-mail com OAuth e acrescentar lembretes e etapas de acompanhamento. Uma integração de candidatura só deve ser criada quando houver API oficial com acesso adequado e consentimento, mantendo revisão das respostas e rastreabilidade do envio.
