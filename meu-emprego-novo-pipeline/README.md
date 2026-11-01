# Método passo a passo: da preparação à contratação

Este é o tutorial do [Agente da Meia Idade](../README.md). Ele ensina a reproduzir, com ajuda de IA, o processo que usei para organizar a minha busca de emprego: perfil-mestre, vagas triadas, currículo sob medida, revisão de cobertura, preparação para entrevista e acompanhamento das candidaturas. O processo terminou em contratação.

> **Este material ensina o método, não expõe a minha vida.** Todos os exemplos usam uma persona fictícia, Ana Souza. Nenhum currículo, contato, recrutador ou empresa real aparece aqui.

---

## Sumário

1. [Para quem é este tutorial](#1-para-quem-é-este-tutorial)
2. [Visão geral](#2-visão-geral)
3. [Vocabulário](#3-vocabulário)
4. [Regras de ouro](#4-regras-de-ouro)
5. [Prepare o ambiente](#5-prepare-o-ambiente)
6. [Passo a passo](#6-passo-a-passo)
7. [Depois da primeira rodada](#7-depois-da-primeira-rodada)
8. [Privacidade: o que nunca versionar](#8-privacidade-o-que-nunca-versionar)
9. [Perguntas frequentes](#9-perguntas-frequentes)
10. [Estrutura da pasta](#10-estrutura-da-pasta)

---

## 1. Para quem é este tutorial

Serve para quem:

- tem experiência real e quer apresentá-la de forma diferente para vagas diferentes, sem inventar nada;
- usa, ou quer usar, um assistente de IA como ferramenta de trabalho, mantendo o controle;
- quer um processo, não uma pilha de PDFs soltos.

Não serve para fabricar experiência, burlar triagem ou candidatar-se em massa sem ler as vagas.

**Ao final, você terá:**

- um perfil-mestre, a fonte de verdade da sua carreira;
- uma lista de exclusões, para nunca reavaliar o que já descartou;
- uma pasta por família de vagas, com currículo, revisão de cobertura e preparação de entrevista;
- um rastreador que mostra o que está funcionando.

## 2. Visão geral

Cada etapa recebe a saída da anterior. A preparação é feita uma vez; as demais se repetem.

| Fase | # | Etapa | Quando | Entrada | Saída |
|---|---|---|---|---|---|
| **Preparar** | 0 | [Princípios](docs/00-principios.md) | Uma vez | | Instruções do assistente |
| | 1 | [Perfil-mestre](docs/01-profile-truth.md) | Uma vez, com ajustes | Sua história real | `profile_truth.md` |
| **Encontrar** | 2 | [Busca de vagas](docs/02-busca-de-vagas.md) | Em rodadas | Perfil + preferências | Lista numerada de vagas |
| | 3 | [Triagem](docs/03-triagem.md) | A cada busca | Lista de vagas | Vagas classificadas por aderência |
| **Candidatar** | 4 | [Currículo sob medida](docs/04-curriculo-sob-medida.md) | Por família de vagas | Perfil + vaga | `resume.json` → `.tex` → PDF |
| | 5 | [Revisão de cobertura](docs/05-coverage-review.md) | Por currículo | Vaga + currículo + perfil | `coverage_review.md` |
| | 6 | [Preparação de entrevista](docs/06-interview-prep.md) | Por vaga | Vaga + currículo + revisão | `interview_prep.md` |
| | 7 | [Candidatura e rastreamento](docs/07-rastreamento.md) | Por candidatura | Candidaturas e respostas | `tracker.csv` |
| **Apoio** | 8 | [Golpes e segurança](docs/08-golpes-e-seguranca.md) | Antes da primeira candidatura | Situações suspeitas | Checklist |
| | 9 | [LinkedIn](docs/09-linkedin.md) | Logo após a etapa 1 | Perfil-mestre | Plano de otimização |
| **Aprender** | 10 | [Resultados e lições](docs/10-resultados-e-licoes.md) | A cada prazo que você definir | Tudo acima | Retrospectiva e ajustes |

Os números são os mesmos dos capítulos em `docs/`. Este README mostra o caminho; cada capítulo aprofunda a etapa, com erros comuns e exemplos.

## 3. Vocabulário

| Termo | O que significa |
|---|---|
| **Perfil-mestre** | O `profile_truth.md`: a versão longa e verdadeira da sua carreira, de onde tudo deriva |
| **Família de vagas** | Grupo de vagas parecidas, como "engenharia de dados" e "backend sênior" |
| **Aderência** | Quanto o seu perfil comprovado atende aos requisitos de uma vaga |
| **Cobertura** | Quais requisitos da vaga o currículo comprova, e com qual evidência |
| **Lacuna** | Requisito que você não comprova. Ela é registrada, nunca disfarçada |
| **ATS** | Sistema que empresas usam para receber e filtrar candidaturas |
| **STAR** | Roteiro de resposta em entrevista: Situação, Tarefa, Ação, Resultado |
| **JSON e LaTeX** | Formatos de arquivo: o JSON guarda o conteúdo do currículo; o LaTeX define o visual e gera o PDF |

## 4. Regras de ouro

Elas valem em todas as etapas. Se precisar improvisar, decida a partir delas.

1. **Uma única fonte de verdade.** Todo currículo deriva do `profile_truth.md`. Se um fato não está lá, não vai para o currículo.
2. **Nunca invente métricas.** Na minha experiência, versões antigas de currículo e de preparação de entrevista acabaram com números divergentes para o mesmo projeto. A revisão de cobertura existe para pegar isso.
3. **A IA propõe, você decide.** Leia tudo o que for enviado em seu nome.
4. **Lacuna declarada vale mais que maquiagem.** Se não tem a habilidade, diga que está aprendendo, ou não se candidate.
5. **Exclusões são regra, não sugestão.** O que está em `vagas_excluidas.md` nunca volta.
6. **Segredos ficam fora do chat.** Senhas, documentos e dados bancários não entram em prompts.
7. **Versione o método, não os dados.** O que é seu fica em `privado/`.

## 5. Prepare o ambiente

### O que você precisa

**Obrigatório**

- Um assistente de IA com contexto persistente. No meu caso foi o Claude com um *Projeto*, onde ficam os arquivos-base, e memória. Funciona com qualquer assistente que permita anexar arquivos e reaproveitar instruções.
- Python 3.9 ou superior. Os scripts usam só a biblioteca padrão.
- Git.

**Para gerar o PDF**

- Uma distribuição LaTeX com `pdflatex`, como TeX Live ou MiKTeX, ou o `tectonic`.

**Opcional, acelera a busca**

- Conectores do assistente para sites de vagas, quando existirem.
- Navegador automatizado para páginas que exigem login. Faça o login você mesmo; nunca entregue senhas ao assistente.

### Instale

Os comandos são para Linux, macOS ou Git Bash no Windows. No Windows, troque `python3` por `python`.

**1. Baixe o repositório e entre na pasta do método:**

```bash
git clone https://github.com/R238Company/meu-emprego-novo.git
cd meu-emprego-novo/meu-emprego-novo-pipeline
```

**2. Crie a sua área privada.** Tudo que for seu fica em `privado/`, que está no `.gitignore` e nunca sobe para o GitHub:

```bash
mkdir -p privado/perfil privado/vagas privado/curriculos privado/entrevistas
cp templates/profile_truth.md privado/perfil/profile_truth.md
cp templates/vagas_excluidas.md privado/vagas/vagas_excluidas.md
cp templates/tracker.csv privado/tracker.csv
```

**3. Teste com a persona de exemplo:**

```bash
python3 scripts/validar_json.py exemplo/resume.json
python3 scripts/json_para_latex.py exemplo/resume.json exemplo/curriculo.tex
pdflatex -output-directory exemplo exemplo/curriculo.tex
```

**Pronto quando:** o primeiro comando mostrar `OK: resume.json válido`, o segundo mostrar `gerado:` e o terceiro criar `exemplo/curriculo.pdf`.

## 6. Passo a passo

Cada etapa abaixo segue o mesmo formato: por que ela existe, o que entra, o que sai, o que fazer e como saber que terminou. **Só avance quando o critério "Pronto quando" estiver cumprido.**

### Fase 1: Preparar

#### Etapa 0: Configure o assistente

**Por que existe:** sem regras escritas, o assistente tende a enfeitar. Com elas, cada conversa já começa dentro dos limites.

**Entrada:** nenhuma. **Saída:** um projeto no assistente com instruções permanentes.

1. Leia os [sete princípios](docs/00-principios.md).
2. Crie um projeto no seu assistente.
3. Cole nas instruções do projeto [o bloco pronto do capítulo 0](docs/00-principios.md#como-aplicar-os-princípios-no-assistente-de-ia) e adapte ao seu caso.

**Pronto quando:** o projeto existir e as instruções disserem que `profile_truth.md` é a única fonte de fatos.

#### Etapa 1: Construa o perfil-mestre

**Por que existe:** é o arquivo mais importante do método. Currículos são versões curtas; o perfil-mestre é a versão completa de onde elas saem. Reserve de 1 a 2 horas.

**Entrada:** currículos antigos, LinkedIn, certificados e memória. **Saída:** `privado/perfil/profile_truth.md`.

1. Para cada empregador, preencha cargo e período e responda: *que problema eu resolvi? como? com quê? qual foi o resultado?*
2. Marque a origem de cada número: `[medido]`, `[estimado]` ou `[sem número]`. Métrica que você não defende em uma entrevista não entra.
3. Registre as lacunas: o que você **não** fez ou apenas estudou. Elas protegem você de respostas inventadas.
4. Anexe o arquivo ao projeto e peça ao assistente que **faça perguntas** para encontrar detalhes esquecidos. Responda apenas o que for verdade.

**Pronto quando:** todo empregador tiver período e resultados, todo número tiver origem e a seção de lacunas estiver preenchida.

**Veja:** [exemplo da Ana](exemplo/profile_truth.md) · [capítulo 1](docs/01-profile-truth.md)

> **Próximo passo recomendado:** com o perfil pronto, faça a [Etapa 9](#etapa-9-alinhe-o-linkedin), para que recrutadores encontrem a mesma história.

### Fase 2: Encontrar

#### Etapa 2: Busque vagas

**Por que existe:** navegar em sites de vagas consome horas. Uma lista padronizada traz, de uma vez, o suficiente para decidir.

**Entrada:** perfil-mestre e critérios de busca. **Saída:** um arquivo por rodada, como `privado/vagas/2026-09-07-linkedin.md`.

1. Antes da primeira busca, preencha `privado/vagas/vagas_excluidas.md` com empresas e tipos de vaga que você não quer. O motivo é só para você. Anexe o arquivo ao projeto.
2. Adapte e use o [prompt de busca](prompts/02-busca-vagas.md). Ele pede resultados com **numeração contínua**, separados em candidatura simplificada e externa, com link, data e requisitos principais.
3. Abra os links. Resultados podem estar desatualizados ou ser anúncios falsos.

**Pronto quando:** você tiver uma lista numerada, só com vagas recentes e com links abertos.

**Por que numerar?** Depois você pode dizer apenas "avalie a 3 e a 7". Veja o [capítulo 2](docs/02-busca-de-vagas.md).

#### Etapa 3: Trie as vagas

**Por que existe:** currículo sob medida dá trabalho. A triagem garante que esse esforço vá para as vagas certas.

**Entrada:** lista de vagas e perfil-mestre. **Saída:** tabela com aderência, evidência, lacunas e decisão.

1. Use o [prompt de triagem](prompts/03-triagem.md). O assistente classifica cada vaga em **alta**, **média** ou **baixa** aderência e cita o trecho do perfil que sustenta a nota. Sem evidência, a nota é só opinião.
2. Revise a tabela. Você decide; a IA só organiza.
3. Descarte sem culpa o que for golpe, presencial fora da sua cidade ou empresa da lista de exclusão. Se o motivo for permanente, atualize `vagas_excluidas.md`.

**Pronto quando:** cada vaga tiver uma decisão: candidatar, decidir depois ou descartar.

**Veja:** [capítulo 3](docs/03-triagem.md), com critérios e sinais de alerta.

### Fase 3: Candidatar

> **Antes da primeira candidatura,** leia a [Etapa 8](#etapa-8-proteja-se-de-golpes). Ela leva poucos minutos e protege você do que mais prejudica nesta fase.

#### Etapa 4: Gere o currículo sob medida

**Por que existe:** a mesma carreira pode ser contada de vários jeitos verdadeiros. O assistente cuida do conteúdo em JSON; um template fixo cuida da forma, então o visual fica sempre consistente.

**Entrada:** perfil-mestre e descrição da vaga. **Saída:** `resume.json`, `curriculo.tex` e `curriculo.pdf`.

Você não precisa de um currículo do zero para cada vaga. O ideal são **4 a 6 versões bem feitas, uma por família de vagas**, com ajustes pontuais. Nomeie as pastas pelo cargo, não pela empresa.

1. Crie a pasta e salve a descrição da vaga em `vaga.md`:
   ```bash
   mkdir -p privado/curriculos/dev-backend
   ```
2. Anexe `templates/resume.json` ao projeto e use o [prompt de currículo](prompts/04-curriculo-sob-medida.md). Salve a resposta em `privado/curriculos/dev-backend/resume.json`.
3. Valide:
   ```bash
   python3 scripts/validar_json.py privado/curriculos/dev-backend/resume.json
   ```
4. Gere o `.tex` e o PDF:
   ```bash
   python3 scripts/json_para_latex.py privado/curriculos/dev-backend/resume.json privado/curriculos/dev-backend/curriculo.tex
   pdflatex -output-directory privado/curriculos/dev-backend privado/curriculos/dev-backend/curriculo.tex
   ```
5. Abra o PDF e **leia inteiro**.

**Pronto quando:** o validador mostrar `OK` e o [checklist de conferência](docs/04-curriculo-sob-medida.md#conferência-final-checklist) estiver completo.

**Veja:** [`resume.json`](exemplo/resume.json) e [PDF](exemplo/curriculo.pdf) da Ana · [capítulo 4](docs/04-curriculo-sob-medida.md)

> **Quer automatizar esta etapa?** A [CLI com agentes](../README.md#5-trilha-b-automatizar-o-currículo-com-a-cli) gera o currículo, um rascunho da revisão e a preparação de entrevista com um comando.

#### Etapa 5: Revise a cobertura

**Por que existe:** se só puder adotar uma prática deste método, adote esta. Quando cada arquivo era gerado separadamente, o mesmo projeto chegou a aparecer com números diferentes. Esta etapa audita o currículo contra a vaga e contra o perfil-mestre.

**Entrada:** vaga, `resume.json` e perfil-mestre. **Saída:** `coverage_review.md`, guardado junto do currículo.

1. Use o [prompt de revisão](prompts/05-coverage-review.md).
2. Comece pelas **lacunas** e **inconsistências**. Corrija no currículo todo fato ou número que não bata com o perfil.
3. Para cada lacuna em requisito obrigatório, decida: candidatar-se mesmo assim e preparar-se para falar dela, ajustar o currículo se for um fato verdadeiro que ficou de fora, ou desistir da vaga.

**Pronto quando:** não houver inconsistência aberta e cada lacuna obrigatória tiver uma decisão sua.

**No exemplo:** a revisão da Ana mostra duas lacunas obrigatórias, Airflow e nuvem em produção. O currículo não as esconde, e ela só se candidata se aceitar falar abertamente sobre a transição. Veja a [revisão completa](exemplo/coverage_review.md) e o [capítulo 5](docs/05-coverage-review.md).

#### Etapa 6: Prepare a entrevista

**Por que existe:** as perguntas são previsíveis, e você responde melhor quando já ensaiou com histórias verdadeiras suas. Se preferir, faça esta etapa só quando uma entrevista for marcada.

**Entrada:** vaga, currículo, revisão de cobertura e perfil-mestre. **Saída:** `interview_prep.md`.

1. Use o [prompt de entrevista](prompts/06-interview-prep.md).
2. Verifique no perfil-mestre cada fato e número. Se aparecer um número que você não reconhece, apague.
3. Escolha de 5 a 6 histórias reais e adapte cada uma a mais de uma pergunta.
4. **Reescreva as respostas com as suas palavras** e ensaie em voz alta. Texto gerado e decorado se desfaz na primeira pergunta de follow-up.
5. Para cada lacuna, prepare uma resposta honesta: *"não tenho experiência direta com X; o mais próximo que fiz foi Y; estou estudando Z"*.

**Pronto quando:** você conseguir contar suas histórias em voz alta, sem ler, e tiver resposta para cada lacuna.

**Veja:** [exemplo da Ana](exemplo/interview_prep.md) · [capítulo 6](docs/06-interview-prep.md), com orientações sobre salário e testes técnicos.

#### Etapa 7: Candidate-se e registre

**Por que existe:** sem registro, você repete erros e não sabe o que prometeu a quem.

**Entrada:** currículo revisado. **Saída:** uma linha nova em `privado/tracker.csv`.

1. Candidate-se **você mesmo**, lendo cada formulário.
2. Nunca preencha número de documento de identidade em formulário de vaga.
3. Registre **logo após** o envio: data, empresa, vaga, fonte, tipo, link, versão do currículo e status.
4. Quando alguém responder, atualize o status e o próximo passo.

**Pronto quando:** toda candidatura enviada tiver uma linha no tracker com a versão do currículo.

**Veja:** [tracker da Ana](exemplo/tracker.csv) · [capítulo 7](docs/07-rastreamento.md), com colunas e métricas.

### Etapas de apoio

#### Etapa 8: Proteja-se de golpes

**Por que existe:** quem procura emprego é alvo de golpes. Encontrei vários desses padrões no meu processo e os transformei em regras, porque regras escritas sobrevivem ao cansaço.

- **Entrevista que pede para baixar e rodar código**, inclusive um repositório "para achar um bug": recuse. Teste técnico legítimo acontece em plataforma conhecida, no navegador.
- **Formulário que pede documento de identidade na candidatura**: deixe em branco e pergunte para que serve. Documento só na contratação, por canal oficial.
- **Pedido de pagamento, taxa ou "kit"**: é golpe.
- **Domínio de e-mail diferente do da empresa**, urgência exagerada, proposta boa demais: desconfie e confirme pelo site oficial.

**Pronto quando:** você tiver lido o [capítulo 8](docs/08-golpes-e-seguranca.md), que traz o checklist antes de aceitar uma entrevista e o que fazer se você já caiu em um golpe.

#### Etapa 9: Alinhe o LinkedIn

**Por que existe:** recrutadores comparam o perfil público com o currículo. Ele precisa contar a mesma história e usar as palavras certas.

**Entrada:** perfil-mestre e texto atual do LinkedIn. **Saída:** `privado/perfil/plano_linkedin.md`.

1. Peça um diagnóstico de inconsistências entre o LinkedIn e o perfil-mestre.
2. Peça 2 ou 3 variações de headline e de "Sobre".
3. Edite com a sua voz e aplique **você mesmo** no site.

**Pronto quando:** datas, cargos e tecnologias baterem com o perfil-mestre.

**Veja:** [capítulo 9](docs/09-linkedin.md), com o que ajustar em cada seção.

### Fase 4: Aprender

#### Etapa 10: Revise e ajuste

**Por que existe:** esta etapa não é o fim do método. É a ferramenta para refinar o seu próprio processo, usada repetidamente: sem ela, você só repete o que já fazia.

**Entrada:** o tracker e a retrospectiva anterior. **Saída:** uma retrospectiva datada e ajustes no perfil-mestre e nos prompts.

1. Defina um prazo para o seu ciclo. Quem escolhe o intervalo é você, conforme a sua rotina.
2. Ao fim do prazo, peça ao assistente um resumo do tracker.
3. Faça a [retrospectiva](docs/10-resultados-e-licoes.md#retrospectiva-repita-a-cada-ciclo) e compare com a anterior: quais versões de currículo geram resposta? Quais fontes de vagas rendem? Onde você desistiu, e por quê?
4. Ajuste o perfil-mestre, os prompts e `vagas_excluidas.md`.
5. Defina o próximo prazo e volte para a [Etapa 2](#etapa-2-busque-vagas).

**Pronto quando:** a retrospectiva gerar pelo menos uma decisão (manter, ajustar ou parar de fazer algo) e o próximo prazo estiver definido.

**Veja:** o [capítulo 10](docs/10-resultados-e-licoes.md) explica como usar os ciclos e traz o que funcionou, o que não funcionou e o que fazer depois da contratação.

## 7. Depois da primeira rodada

A preparação não se repete. A partir daqui, o ciclo é:

```
busca → triagem → currículo (reaproveite a versão da família) → revisão → entrevista → registro → ajustes
```

Três hábitos mantêm o processo sustentável:

- **Corrija sempre na fonte.** Mudou um fato? Altere o perfil-mestre, não cada currículo.
- **Peça só vagas novas.** Informe a data da última busca para não rever o que já avaliou.
- **Defina um ritmo.** Busca de emprego é maratona: estabeleça horários, pausas e um limite de candidaturas por dia.

## 8. Privacidade: o que nunca versionar

Mesmo com `.gitignore`, confira antes de publicar. Nunca suba:

- currículos reais (JSON, TeX, PDF) e o `profile_truth.md` real;
- telefone, e-mail pessoal, endereço e links de perfil pessoais;
- nomes de recrutadores, e-mails e mensagens recebidas;
- pretensão salarial, ofertas e valores combinados;
- planilhas de contatos;
- opiniões sobre empresas identificáveis;
- números de documentos de identificação ou de cartões.

Antes de cada commit, rode:

```bash
bash scripts/checar_privacidade.sh
```

O script procura e-mails, telefones, CPFs e perfis de LinkedIn nesta pasta, ignorando `privado/`, e avisa se achar algo. Ele não substitui a sua leitura.

Se algo sensível já foi commitado, **não adianta apagar no commit seguinte**: o histórico guarda tudo. Recrie o repositório do zero ou reescreva o histórico antes de publicar.

## 9. Perguntas frequentes

**Preciso usar o mesmo assistente que você?** Não. O método só exige que o assistente leia seus arquivos-base e siga instruções estáveis.

**Posso usar em outra profissão?** Sim. Troque a persona e os exemplos; as etapas são as mesmas.

**Preciso saber programar?** Não para o método. Os scripts são três comandos que você copia e cola. Só a [CLI com agentes](../README.md#5-trilha-b-automatizar-o-currículo-com-a-cli) exige familiaridade com terminal e API.

**Quantas versões de currículo devo ter?** Uma por família de vagas, não uma por vaga. Ajuste só o necessário por candidatura.

**A IA vai deixar meu currículo com cara de robô?** Pode. Reescreva o resumo e os destaques com a sua voz.

**Posso confiar nas vagas que o assistente encontra?** Confira link, empresa e data. Resultados de busca podem estar desatualizados ou ser golpes.

**Posso pular etapas?** Na pressa, mantenha ao menos o perfil-mestre (etapa 1), a revisão de cobertura (etapa 5) e o registro (etapa 7). São elas que protegem você de enviar algo falso e de repetir erros.

## 10. Estrutura da pasta

```
meu-emprego-novo-pipeline/
├── README.md                    # este tutorial
├── docs/                        # capítulos de aprofundamento (00 a 10)
├── prompts/                     # prompts das etapas 2 a 6, prontos para adaptar
├── templates/                   # arquivos em branco para começar
│   ├── profile_truth.md
│   ├── resume.json
│   ├── vagas_excluidas.md
│   └── tracker.csv
├── scripts/
│   ├── validar_json.py          # confere campos obrigatórios do resume.json
│   ├── json_para_latex.py       # converte resume.json em .tex
│   └── checar_privacidade.sh    # procura dados pessoais antes do commit
├── exemplo/                     # fluxo completo da persona Ana Souza
└── privado/                     # SUA área (criada por você, nunca versionada)
```

---

Para contribuir, veja o [CONTRIBUTING.md](../CONTRIBUTING.md). Licença MIT: veja [LICENSE](LICENSE). Use, adapte e compartilhe. Se este material ajudar você a conseguir uma vaga, conte a sua história em uma issue.
