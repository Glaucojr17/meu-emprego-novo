# 02. Busca de vagas

## Objetivo
Obter listas de vagas **numeradas, organizadas e com informação suficiente para decidir**, sem gastar horas navegando.

## Entrada
- `profile_truth.md`
- `vagas_excluidas.md`
- Critérios: modalidade (remoto/híbrido/presencial), localização, senioridade, faixa de interesse, tipo de contrato.

## Saída
Um arquivo por rodada de busca, por exemplo `privado/vagas/2026-09-07-linkedin.md`, com as vagas agrupadas.

## Formato recomendado dos resultados

Peça sempre este formato, porque ele facilita as próximas etapas:

```
## Candidatura simplificada (dentro da plataforma)
1. Título: ... | Empresa: ... | Local/modalidade: ... | Publicada em: ... | Link: ...
   Requisitos principais: ...
2. ...

## Candidatura externa (site da empresa / ATS)
3. ...
4. ...
```

A **numeração contínua** entre os grupos permite instruções curtas como "avalie a 2, a 5 e a 8". Separar simplificada de externa ajuda a planejar o esforço: externa costuma exigir cadastro e formulários longos.

## Onde buscar
- Plataformas de vagas com filtros de data e modalidade.
- Sites de carreira de empresas-alvo.
- Vagas internacionais remotas (vale uma lista separada, com atenção a fuso horário, idioma falado e tipo de contratação).
- Alertas por e-mail e notificações. Se vier um link de coleção ou de recomendações, peça ao assistente que avalie as vagas da página, uma a uma.

## Como usar o assistente na busca
1. Informe os critérios e peça que consulte `vagas_excluidas.md`.
2. Peça só vagas **publicadas desde a última busca** (informe a data).
3. Peça os requisitos principais de cada vaga em 1 ou 2 linhas.
4. Em sites que exigem login, faça o login você mesmo no navegador; o assistente só opera depois.
5. Confira sempre o link: resultados podem estar desatualizados ou serem anúncios falsos.

## Lista de exclusões (`vagas_excluidas.md`)
Mantenha um arquivo com empresas/tipos de vaga que não devem aparecer, e o motivo **só para você**. Exemplos de motivos legítimos:

- experiência anterior ruim com a empresa;
- vaga alocada em cliente final que você não quer;
- vaga que parece golpe;
- modalidade incompatível (por exemplo, 100% presencial em outra cidade).

> Não publique esse arquivo. Opiniões sobre empresas identificáveis são problema jurídico e de reputação.

## Erros comuns
- Buscar sem data e receber vaga velha.
- Aceitar a descrição do assistente sem abrir o link.
- Não registrar por que descartou uma vaga (você vai rever a mesma).
- Misturar buscas de dias diferentes no mesmo arquivo.

## Prompt
[`prompts/02-busca-vagas.md`](../prompts/02-busca-vagas.md)
