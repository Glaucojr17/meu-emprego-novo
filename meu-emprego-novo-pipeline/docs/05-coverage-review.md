# 05. Revisão de cobertura (`coverage_review.md`)

## Objetivo
Auditar o currículo gerado contra **duas** coisas:
1. a vaga (o que ela pede e o que está coberto);
2. o perfil-mestre (o que foi dito é verdadeiro).

É a etapa que impede que o assistente "enfeite" demais.

## Entrada
`vaga.md`, `resume.json`, `profile_truth.md`.

## Saída
`coverage_review.md` com cinco blocos:

1. **Fontes usadas**: quais arquivos foram considerados.
2. **Preservado**: empregadores, cargos, datas e quantidade de destaques mantidos.
3. **Cobertura forte**: requisitos da vaga com evidência clara no currículo.
4. **Cobertura parcial**: requisitos tocados indiretamente.
5. **Lacunas não inventadas**: requisitos que o currículo **não** comprova, listados nominalmente.

E uma declaração final no estilo: *"Esta revisão não afirma que todos os requisitos obrigatórios são atendidos."*

## Por que isso importa
Em versões iniciais do meu processo, currículos e materiais de entrevista chegaram a mostrar números diferentes para o mesmo projeto, porque cada arquivo foi gerado separadamente. A revisão de cobertura passou a comparar tudo com o perfil-mestre e a remover o que não tinha lastro. Se você só puder adotar uma prática deste repositório, adote esta.

## Passo a passo
1. Rode o prompt de [`prompts/05-coverage-review.md`](../prompts/05-coverage-review.md).
2. Leia a seção de lacunas primeiro.
3. Para cada lacuna obrigatória, decida:
   - **candidatar-se mesmo assim** (e se preparar para falar sobre isso);
   - **ajustar o currículo** (se for um fato verdadeiro que ficou de fora; atualize o perfil-mestre);
   - **desistir da vaga**.
4. Guarde o arquivo junto do currículo. Ele vira insumo para a preparação da entrevista.

## Erros comuns
- Tratar a revisão como carimbo de aprovação. Ela é um relatório de risco.
- Aceitar "cobertura forte" sem conferir a evidência.
- Esconder lacuna obrigatória. A entrevista técnica vai descobrir.

## Exemplo
[`exemplo/coverage_review.md`](../exemplo/coverage_review.md)
