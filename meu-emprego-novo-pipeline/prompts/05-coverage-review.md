# Prompt: revisão de cobertura

```
Faça uma auditoria de resume.json contra vaga.md e profile_truth.md.

Produza coverage_review.md com os blocos:

1. Fontes usadas.
2. Preservado: empregadores, cargos, datas e número de destaques mantidos.
3. Cobertura forte: requisito da vaga -> trecho do currículo -> trecho do perfil que comprova.
4. Cobertura parcial: o que está tocado só indiretamente.
5. Lacunas não inventadas: requisitos que o currículo NÃO comprova (liste por nome).
6. Inconsistências: qualquer fato, data ou número do currículo que não bata com o perfil.
7. Declaração final: "Esta revisão não afirma que todos os requisitos obrigatórios são atendidos."

Regras:
- Se não houver evidência no perfil, diga "sem evidência".
- Não sugira acrescentar o que é lacuna; sugira apenas reordenar ou, se for fato verdadeiro omitido, indicar atualizar o perfil.
```
