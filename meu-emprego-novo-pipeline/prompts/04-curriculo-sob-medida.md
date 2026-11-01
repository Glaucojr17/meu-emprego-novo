# Prompt: currículo sob medida (JSON)

Use para criar a **primeira versão de uma família de vagas**. Para adaptar uma versão que já existe, use [`04b-ajustar-curriculo.md`](04b-ajustar-curriculo.md).

Anexe `profile_truth.md`, `templates/resume.json` e a descrição da vaga em `vaga.md`.

```
Gere resume.json para a vaga em vaga.md, no formato de templates/resume.json.

Fontes:
- profile_truth.md é a ÚNICA fonte de fatos, inclusive dos dados de contato.
- vaga.md define o que priorizar.

Regras obrigatórias:
1. Preserve todos os empregadores, cargos e datas reais.
2. Não invente tecnologias, métricas, certificações ou responsabilidades.
3. Use números apenas se estiverem marcados [medido] no perfil.
4. Reordene e reescreva os destaques para priorizar o que a vaga pede.
5. Use o vocabulário da vaga somente quando for verdadeiro para mim.
6. Certificações com a situação real (válida, expirada, em andamento).
7. Resumo com 3 a 4 linhas.
8. Máximo de [N] destaques por empresa recente e [M] nas antigas.
9. Datas no formato AAAA-MM. No emprego atual, use "Present" em endDate.
10. Campo sem informação no perfil fica vazio; nunca deduza.

Responda somente com o JSON puro: sem texto antes ou depois, sem comentários e sem bloco de código.
```

Sugestão para `[N]` e `[M]`: de 3 a 5 destaques nas empresas recentes e menos nas antigas.

Depois de salvar o arquivo, envie uma segunda mensagem:

```
Liste em até 5 linhas o que você enfatizou e o que deixou em segundo plano.
```
