# Prompt: ajustar uma versão para outra vaga da mesma família

Use quando a revisão de cobertura mostrar que uma versão existente precisa de um ajuste pontual.

Anexe o `resume.json` da versão atual, `profile_truth.md`, `vaga.md` e `coverage_review.md`.

```
Crie uma nova versão de resume.json, partindo do arquivo anexado, para a vaga em vaga.md.

Fontes:
- profile_truth.md é a ÚNICA fonte de fatos.
- coverage_review.md indica o que precisa mudar.

Regras obrigatórias:
1. Altere apenas o necessário: ordem dos destaques, ordem das competências e o resumo.
2. Preserve todos os empregadores, cargos e datas.
3. Só acrescente um destaque se o fato estiver em profile_truth.md.
4. Não tente cobrir as lacunas da revisão. Lacuna continua sendo lacuna.
5. Use números apenas se estiverem marcados [medido] no perfil.

Responda somente com o JSON puro: sem texto antes ou depois, sem comentários e sem bloco de código.
```

Depois de salvar o arquivo, envie uma segunda mensagem:

```
Liste o que mudou em relação à versão anterior, em até 5 linhas.
```
