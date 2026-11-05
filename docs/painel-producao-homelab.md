# Painel de vagas no homelab — instalação na devops-ci

Esta aplicação é de uso pessoal. Ela coleta vagas de APIs públicas permitidas e de alertas próprios, organiza uma fila e prepara documentos a partir de `data/glaucojunior/resume.json`. **Não envia candidaturas.** Uma vaga marcada como `candidatada` é apenas um registro feito por você no painel.

O painel só escuta em `127.0.0.1:8000` dentro da VM e é aberto no Windows por túnel SSH. Dados, tokens, currículo, PDFs e banco SQLite ficam fora do Git. Não publique nem copie `input/`, `data/` ou `outputs/` para repositórios públicos.

## 1. Preparar a VM

No PowerShell do Windows:

```powershell
$key = Join-Path $env:USERPROFILE '.ssh\id_ed25519_lab_ops'
ssh -i $key glaucojunior@10.77.10.21
```

Os comandos a seguir são no Debian, com o usuário `glaucojunior`:

```bash
cd ~/projetos/meu-emprego-novo
git pull --ff-only
sudo apt update
sudo apt install -y python3-venv
python3 -m venv .venv-platform
.venv-platform/bin/python -m pip install -r requirements-platform.txt
.venv-platform/bin/python -m unittest tests.test_opportunities tests.test_platform_app -v
```

O esperado é `OK`. Esse ambiente virtual é separado da instalação opcional do CrewAI e funciona com Python 3.13 do Debian 13. Se o projeto ainda não estiver clonado, siga primeiro [o guia inicial](devops-ci-setup.md).

## 2. Configurar fontes e perfil

```bash
mkdir -p input/glaucojunior/job_alerts data/glaucojunior
chmod 700 input/glaucojunior data/glaucojunior
cp -n examples/opportunities/job_policy.example.json input/glaucojunior/job_policy.json
cp -n examples/opportunities/platform.example.json input/glaucojunior/platform.json
nano input/glaucojunior/job_policy.json
nano input/glaucojunior/platform.json
```

No `job_policy.json`, ajuste títulos, tecnologias, exclusões e `remote_only`. No `platform.json`:

- `himalayas_queries` consulta a API pública da Himalayas com filtro `country=BR` e até cinco termos. O exemplo usa DevOps, SRE e Infrastructure. Há cache de 24 horas. O link de candidatura e o crédito visível usam a própria Himalayas.
- `devops_brasil: true` consulta issues abertas do quadro comunitário DevOps Brasil (cache de 6 horas). A data da issue é a data do anúncio no quadro; confirme no link se a seleção continua aberta.
- `remotive: false` deixa desligada a fonte internacional que trouxe muitos anúncios em inglês. Se ativá-la, a resposta é guardada por 6 horas para respeitar o limite recomendado; a fonte e o link direto aparecem no painel.
- `brazil_only: true` exige Brasil, LATAM ou abrangência mundial informada no campo de localização. País incerto fica para revisão.
- `require_portuguese: true` exige sinais de texto em português na descrição. É uma heurística, então pode deixar de priorizar um anúncio bilíngue; altere para `false` se quiser considerar vagas em inglês que aceitam pessoas no Brasil.
- `max_age_days: 30` tira vagas datadas há mais de 30 dias do filtro **Aderentes**. A data de publicação é exibida quando a fonte a oferece; quando há somente data de atualização, o painel indica **Atualizada em**. Data ausente é explicitada e exige sua conferência.
- `greenhouse_boards` e `lever_sites` recebem os identificadores das páginas de carreiras das empresas que você escolher acompanhar. Exemplo: `["empresaexemplo"]`, após confirmar que a empresa usa esse identificador. São consultas públicas por empresa.
- `arbeitnow` começa desligado porque concentra vagas europeias.
- `gmail_query` começa vazio. Você pode ativar depois, por exemplo com `"label:Vagas newer_than:14d"`, após criar e alimentar essa etiqueta no Gmail e concluir o OAuth.
- `max_new_documents_per_run` limita a quantidade de PDFs novos em cada coleta.

O PDF requer seu **currículo mestre validado** em `data/glaucojunior/resume.json`. Ele segue a estrutura de `examples/dev_procurando/resume.json`, mas **não copie dados fictícios como se fossem seus**. Se já preparou o arquivo com a ferramenta original, confira nome, empresas, datas, experiências e tecnologias. Se ainda não preparou, siga a seção 5 do [guia inicial](devops-ci-setup.md) para extrair do seu currículo e revisar o JSON. O painel pode coletar vagas sem esse arquivo, mas exibirá a pendência e não criará documentos.

Também aceita seus próprios alertas `.eml` em `input/glaucojunior/job_alerts/` e links diretos em `input/glaucojunior/vagas.csv`, conforme [a triagem anterior](opportunities.md). Não usa bots em LinkedIn ou Gupy.
O CSV pode incluir uma coluna opcional `published_at` em formato `AAAA-MM-DD`, se você confirmou a data no anúncio. Não preencha com a data do e-mail.

### Atualizar uma instalação já em uso

`git pull --ff-only` não altera seus arquivos privados em `input/` nem o banco. A migração do SQLite preserva status e anotações. Para aplicar o exemplo refinado ao perfil que antes usava Remotive, guarde as preferências atuais e execute:

```bash
cd ~/projetos/meu-emprego-novo
cp -p input/glaucojunior/platform.json input/glaucojunior/platform.json.pre-filtro-br
cp -p input/glaucojunior/job_policy.json input/glaucojunior/job_policy.json.pre-filtro-br
python3 - <<'PY'
import json
from pathlib import Path
p = Path("input/glaucojunior/platform.json")
data = json.loads(p.read_text(encoding="utf-8"))
data.update(remotive=False, himalayas_queries=["DevOps", "SRE", "Infrastructure"],
            devops_brasil=True, brazil_only=True, require_portuguese=True,
            max_age_days=30)
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
cp examples/opportunities/job_policy.example.json input/glaucojunior/job_policy.json
chmod 600 input/glaucojunior/platform.json input/glaucojunior/job_policy.json
python3 -m json.tool input/glaucojunior/platform.json >/dev/null
python3 -m json.tool input/glaucojunior/job_policy.json >/dev/null
.venv-platform/bin/python -m src.platform_app run --person glaucojunior
sudo systemctl restart meu-emprego-painel.service
```

O exemplo da política foca DevOps, SRE e infraestrutura; se você tinha termos próprios, reaplique-os após comparar com o backup. A tela abre em **Aderentes**; selecione **Todas** para auditar anúncios descartados. Se não houver currículo mestre, mantenha `max_new_documents_per_run: 0` como já configurado. Vagas antigas continuam registradas, mas deixam de aparecer como aderentes quando excedem a janela configurada.

## 3. Executar uma coleta manual

```bash
cd ~/projetos/meu-emprego-novo
.venv-platform/bin/python -m src.platform_app run --person glaucojunior
cat outputs/glaucojunior/platform/last-run.json
```

O comando informa total recebido, novas vagas, quantidade aderente, PDFs gerados e erros por fonte. Uma fonte indisponível não apaga as demais vagas. Se o currículo mestre ainda não existir, mantenha `max_new_documents_per_run: 0`; do contrário aparecerá `FileNotFoundError` por documento. Os arquivos ficam em `outputs/glaucojunior/platform/documents/<id>/`, e o banco em `outputs/glaucojunior/platform/jobs.sqlite3`.

A adaptação gratuita seleciona e prioriza experiências e habilidades **já existentes no JSON mestre**, sem inventar cargos, resultados ou tecnologias. O resumo acrescenta somente termos com evidência no currículo; o roteiro traz exemplos existentes e lacunas para você confirmar. A qualidade depende do JSON mestre. Leia o PDF antes de enviar.

## 4. Subir o painel como serviço

Crie um segredo para autenticação no terminal Debian:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(24))'
nano input/glaucojunior/platform.env
```

No arquivo, coloque as três linhas abaixo, substituindo o valor da senha pelo segredo gerado:

```ini
PLATFORM_PERSON=glaucojunior
PLATFORM_USER=glaucojunior
PLATFORM_PASSWORD=COLE_AQUI_O_SEGREDO_GERADO
```

```bash
chmod 600 input/glaucojunior/platform.env
sudo cp deploy/systemd/meu-emprego-painel.service deploy/systemd/meu-emprego-coleta.service deploy/systemd/meu-emprego-coleta.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now meu-emprego-painel.service
sudo systemctl enable --now meu-emprego-coleta.timer
systemctl status meu-emprego-painel.service --no-pager
systemctl list-timers meu-emprego-coleta.timer --no-pager
```

O timer roda às 07h **do relógio configurado na VM**. Confira `timedatectl`; ajuste o fuso da VM se necessário. O `Persistent=true` tenta executar uma coleta perdida quando a VM voltar a ligar. Para disparar antes do horário:

```bash
sudo systemctl start meu-emprego-coleta.service
journalctl -u meu-emprego-coleta.service -n 80 --no-pager
```

Se houver erros em alguma fonte, o serviço registra falha e o log informa qual foi. Resultados obtidos de outras fontes continuam salvos.

## 5. Abrir o painel no Windows

Em **outra janela do PowerShell**, deixe um túnel SSH aberto:

```powershell
$key = Join-Path $env:USERPROFILE '.ssh\id_ed25519_lab_ops'
ssh -i $key -N -L 8000:127.0.0.1:8000 glaucojunior@10.77.10.21
```

No navegador do Windows, abra **http://127.0.0.1:8000** e informe usuário `glaucojunior` e a senha de `platform.env`. A janela do túnel precisa permanecer aberta. O painel tem botão de coleta manual, filtros, detalhes, PDF, roteiro e status para seu acompanhamento. A porta 8000 não é exposta na rede da VM.

## 6. Gmail automático (opcional)

Esta etapa exige uma configuração **sua** no Google Cloud; a conexão do Gmail no ChatGPT não transfere credenciais para sua VM. Siga o [quickstart oficial da API Gmail](https://developers.google.com/workspace/gmail/api/quickstart/python): crie um projeto, habilite Gmail API, configure a tela de consentimento para uso pessoal, adicione sua conta como usuário de teste se necessário e crie um cliente OAuth **Desktop app**. Baixe o JSON para o Windows e copie para a VM:

```powershell
$key = Join-Path $env:USERPROFILE '.ssh\id_ed25519_lab_ops'
$credencial = 'C:\Users\Glauco\Downloads\client_secret.json'
scp -i $key $credencial 'glaucojunior@10.77.10.21:/home/glaucojunior/projetos/meu-emprego-novo/input/glaucojunior/google-credentials.json'
```

Na VM, instale os pacotes opcionais e proteja o arquivo:

```bash
cd ~/projetos/meu-emprego-novo
chmod 600 input/glaucojunior/google-credentials.json
.venv-platform/bin/python -m pip install -r requirements-platform-gmail.txt
```

Abra **outro** PowerShell com um túnel para o callback OAuth:

```powershell
$key = Join-Path $env:USERPROFILE '.ssh\id_ed25519_lab_ops'
ssh -i $key -N -L 8765:127.0.0.1:8765 glaucojunior@10.77.10.21
```

No terminal da VM, execute `.venv-platform/bin/python -m src.platform_app auth-gmail --person glaucojunior`. Copie a URL mostrada para o navegador do Windows, autorize o acesso **somente leitura** e aguarde o retorno ao `localhost:8765`. O token privado ficará em `input/glaucojunior/gmail-token.json`. Depois, defina `gmail_query` no `platform.json` e faça nova coleta. Feche o túnel 8765 quando terminar.

Alguns e-mails contêm apenas links de rastreamento que a ferramenta não consegue resolver. Nesses casos, registre o link direto no CSV privado. O acesso Gmail usa apenas `gmail.readonly`; não envia mensagens.

## 7. Manutenção e verificação

```bash
cd ~/projetos/meu-emprego-novo
git status --short
git check-ignore input/glaucojunior/platform.env data/glaucojunior/resume.json outputs/glaucojunior/platform/jobs.sqlite3
systemctl status meu-emprego-painel.service --no-pager
journalctl -u meu-emprego-painel.service -n 50 --no-pager
df -h /
```

Faça backup privado de `input/`, `data/` e `outputs/`. Para atualizar o código, rode `git pull --ff-only`, reinstale as dependências se `requirements-platform*.txt` mudar e reinicie o painel. O timer não precisa de navegador aberto; a VM precisa estar ligada e com internet para consultar as fontes.
