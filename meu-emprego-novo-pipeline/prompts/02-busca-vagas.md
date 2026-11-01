# Prompt: busca de vagas

Adapte os campos entre `[colchetes]`.

```
Busque vagas no [LinkedIn / Indeed / site X] com estes critérios:
- Cargos: [lista]
- Modalidade: [remoto / híbrido / presencial em CIDADE]
- Local: [Brasil / LATAM / mundo]
- Publicadas desde: [AAAA-MM-DD]

Antes de buscar, leia vagas_excluidas.md e não inclua nada que esteja lá.
Use profile_truth.md para descartar vagas claramente incompatíveis.

Formato da resposta:
1. Dois grupos: "Candidatura simplificada" e "Candidatura externa".
2. Numeração contínua entre os grupos.
3. Para cada vaga: título | empresa | local/modalidade | data de publicação | link.
4. Abaixo, em 1 ou 2 linhas, os requisitos principais.
5. No fim, liste o que você descartou e por quê.

Não se candidate a nada. Não use dados de documentos.
```
