# Rodar o projeto na VM devops-ci

Este roteiro foi escrito para a VM Debian 13 `devops-ci` do homelab. Execute os comandos Linux **como o usuário `glaucojunior`**, conectado por SSH em `10.77.10.21`. O código fica no disco da VM, em `~/projetos/meu-emprego-novo`; dados pessoais permanecem somente nas pastas locais ignoradas pelo Git.

## 1. Acessar a VM pelo Windows

No PowerShell do Windows:

```powershell
$key = Join-Path $env:USERPROFILE '.ssh\id_ed25519_lab_ops'
ssh -i $key glaucojunior@10.77.10.21
```

Se a chave ainda não estiver autorizada nessa VM, use `ssh glaucojunior@10.77.10.21` e a senha da conta. Verifique no terminal Linux:

```bash
id -un
hostname
python3 --version
git --version
df -h /
```

Espere `glaucojunior`, `devops-ci` e Python 3.13. Não rode a instalação como root.

## 2. Baixar o seu fork e testar a triagem

```bash
mkdir -p ~/projetos
cd ~/projetos
git clone https://github.com/Glaucojr17/meu-emprego-novo.git
cd meu-emprego-novo
python3 -m unittest tests.test_opportunities -v
```

Os três testes devem terminar com `OK`. Se a pasta já existir, entre nela e rode `git pull --ff-only` antes de testar. Este módulo usa apenas a biblioteca padrão do Python; nesta etapa não precisa instalar `requirements.txt` ou fornecer chave de IA.

## 3. Criar suas preferências privadas

```bash
mkdir -p input/glaucojunior/job_alerts
cp -n examples/opportunities/job_policy.example.json input/glaucojunior/job_policy.json
if [ ! -e input/glaucojunior/vagas.csv ]; then
    printf 'source,url,title,company,location,description\n' > input/glaucojunior/vagas.csv
fi
nano input/glaucojunior/job_policy.json
```

Ajuste os títulos e termos que descrevem vagas que você realmente quer. O exemplo prioriza DevOps, SRE, infraestrutura e trabalho remoto. `remote_only: true` exige menção explícita de remoto nos dados disponíveis; vagas sem essa informação ficam pendentes de revisão. O filtro por palavras-chave não verifica requisitos completos.

Para adicionar uma vaga, edite `nano input/glaucojunior/vagas.csv` e acrescente **uma linha com dados reais**. Use um link direto de vaga `https://www.linkedin.com/jobs/view/ID/` ou `https://empresa.gupy.io/jobs/ID`. Se a descrição tiver vírgulas, coloque esse campo entre aspas. Não copie a vaga fictícia de `examples/` para sua lista de trabalho.

Outra opção: salve seus alertas de vagas recebidos por e-mail como arquivos `.eml` em `input/glaucojunior/job_alerts/`. Exemplo de cópia de um alerta do Windows para a VM:

```powershell
$key = Join-Path $env:USERPROFILE '.ssh\id_ed25519_lab_ops'
$alerta = 'C:\Users\Glauco\Downloads\alerta-de-vaga.eml'
scp -i $key $alerta 'glaucojunior@10.77.10.21:/home/glaucojunior/projetos/meu-emprego-novo/input/glaucojunior/job_alerts/'
```

Substitua o caminho do arquivo pelo nome real. Alguns e-mails usam links de rastreamento: nesse caso, abra a vaga normalmente e informe o link direto no CSV. A ferramenta não entra nas plataformas para buscar anúncios.

## 4. Gerar o primeiro relatório

Na VM, dentro de `~/projetos/meu-emprego-novo`:

```bash
python3 -m src.opportunities --person glaucojunior scan
cat outputs/glaucojunior/opportunities/relatorio.md
```

Sem alertas ou linhas de vagas, o resultado esperado é `0 vagas únicas`. Com uma vaga válida, revise pontuação, link, empresa e regime antes de decidir candidatar-se. O CSV gerado está em `outputs/glaucojunior/opportunities/vagas.csv`. A mesma URL recebida por e-mail e cadastrada manualmente aparece uma só vez.

## 5. Preparar currículo e entrevista com IA (opcional)

Esta parte é do projeto original e faz chamadas pagas ou sujeitas às condições do provedor escolhido. O README recomenda Python 3.12. No Debian 13, mantenha o Python 3.13 do sistema e instale 3.12 isoladamente com `uv`:

```bash
sudo apt update
sudo apt install -y pipx
pipx install uv
~/.local/bin/uv python install 3.12
cd ~/projetos/meu-emprego-novo
~/.local/bin/uv venv --python 3.12 .venv
~/.local/bin/uv pip install --python .venv/bin/python -r requirements.txt
~/.local/bin/uv pip install --python .venv/bin/python python-docx
.venv/bin/python --version
```

Se `pipx install uv` disser que já está instalado, siga para `uv python install`. A última linha deve mostrar Python 3.12. Se a instalação de dependências falhar, guarde a mensagem exata para diagnosticar; a triagem das etapas 2–4 continua independente.

Prepare a configuração, sem publicar sua chave:

```bash
cp -n .env.example .env
chmod 600 .env
nano .env
```

No `.env`, configure `PERSON=glaucojunior`, altere o padrão `LLM_PROVIDER=bedrock` para o provedor que você realmente usa e preencha **somente** a variável de chave correspondente. Você não precisa de assinatura Azure para isso. Não coloque a chave em mensagens, comandos salvos no histórico ou no GitHub.

Copie seu currículo PDF/DOCX verdadeiro para `input/glaucojunior/` e crie `input/glaucojunior/profile_truth.md` com cargos, empresas, datas e tecnologias confirmados. O modelo está em `meu-emprego-novo-pipeline/templates/profile_truth.md`. O envio de documentos à IA ocorre ao rodar a ingestão:

```bash
mkdir -p data/glaucojunior
.venv/bin/python -m src.scripts.ingest_resume --person glaucojunior
nano data/glaucojunior/resume.json
```

Revise o JSON antes de prosseguir. Rodar `ingest_resume` novamente pode sobrescrever suas correções. Copie a **descrição completa** de uma vaga para `input/glaucojunior/job_desc.md` e execute:

```bash
.venv/bin/python main.py --person glaucojunior --job input/glaucojunior/job_desc.md
find outputs/glaucojunior -name interview_prep.md -o -name output_resume.pdf
```

O roteiro de entrevista e o currículo gerados são rascunhos: confira cada experiência e ajuste sua fala. Nenhuma candidatura é enviada por esse comando.

## 6. Registrar uma candidatura concluída

Depois de se candidatar no site, salve o comprovante em `input/glaucojunior/` e rode:

```bash
python3 -m src.opportunities --person glaucojunior record \
  --url https://empresa.gupy.io/jobs/123456 \
  --title 'Analista DevOps' \
  --evidence input/glaucojunior/comprovante-123456.png
python3 -m src.opportunities --person glaucojunior scan
```

Substitua URL, título e arquivo pelos dados reais. `outputs/glaucojunior/opportunities/historico.json` guarda a confirmação; o relatório distingue vaga encontrada de candidatura registrada. Para atualizar o código depois, use `git pull --ff-only` na pasta do projeto. Faça backup privado de `input/`, `data/` e `outputs/`; essas pastas não vão para o GitHub.
