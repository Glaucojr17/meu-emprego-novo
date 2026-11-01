# Prompt: currículo sob medida (JSON)

```
Gere resume.json para a vaga em vaga.md, no formato de templates/resume.json.

Fontes:
- profile_truth.md é a ÚNICA fonte de fatos.
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
9. Saída: apenas JSON válido, sem comentários.

Depois do JSON, liste em até 5 linhas o que você enfatizou e o que deixou em segundo plano.
```
