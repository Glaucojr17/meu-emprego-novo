# A busca da Ana: o método do início ao fim

Ana Souza é uma persona fictícia: uma desenvolvedora backend com 7 anos de experiência, em transição para engenharia de dados. Esta pasta mostra a busca dela e tem **a mesma estrutura que a sua `privado/` terá**. Use-a como modelo de resultado para cada etapa.

## Siga a história

| Etapa | O que a Ana fez | Veja |
|---|---|---|
| 1. Perfil-mestre | Escreveu a carreira, marcou a origem dos números e registrou as lacunas | [profile_truth.md](perfil/profile_truth.md) |
| 2. Busca | Definiu exclusões e buscou vagas numeradas | [exclusões](vagas/vagas_excluidas.md) · [busca](vagas/2026-09-07-busca.md) |
| 3. Triagem | Classificou as 4 vagas e descartou 1 | [triagem](vagas/2026-09-07-triagem.md) |
| 4. Currículo | Criou a `dados-v1` para a família de dados | [resume.json](curriculos/dados/v1/resume.json) · [PDF](curriculos/dados/v1/curriculo.pdf) |
| 5. Revisão | Encontrou duas lacunas obrigatórias na vaga da Delta | [revisão](curriculos/dados/vagas/2026-09-10-empresa-delta/coverage_review.md) |
| 6. Entrevista | Preparou respostas honestas para as lacunas | [preparação](curriculos/dados/vagas/2026-09-10-empresa-delta/interview_prep.md) |
| 7. Registro | Registrou cada candidatura com a versão do currículo | [tracker](tracker.csv) |
| 8. Segurança | Descartou a Zeta ao ver que o teste exigia executar código | [tracker](tracker.csv) · [exclusões](vagas/vagas_excluidas.md) |
| 9. LinkedIn | Corrigiu um cargo que ela nunca ocupou | [plano](perfil/plano_linkedin.md) |
| 10. Retrospectiva | Ao fim do prazo de 2 semanas, decidiu mudar o tipo de vaga | [retrospectiva](retrospectivas/2026-09-21.md) |

## O segundo ciclo

A retrospectiva mudou a busca, e é aqui que o método mostra o seu valor:

1. A [nova busca](vagas/2026-09-22-busca.md) encontrou uma vaga na Empresa Teta, da mesma família.
2. A Ana salvou a [vaga](curriculos/dados/vagas/2026-09-23-empresa-teta/vaga.md) em uma nova pasta e revisou a `dados-v1` contra ela.
3. A [revisão](curriculos/dados/vagas/2026-09-23-empresa-teta/coverage_review.md) mostrou que bastava um ajuste pontual.
4. Ela criou a [`dados-v2`](curriculos/dados/v2/resume.json), que reordena os destaques e usa um fato registrado nos [adendos do perfil](perfil/profile_truth.md#adendos-detalhes-lembrados-depois).
5. Registrou no [tracker](tracker.csv) que enviou a `dados-v2`.

## Como a pasta está organizada

```
exemplo/
├── perfil/                   # profile_truth.md e plano do LinkedIn
├── vagas/                    # exclusões, buscas e triagens, por data
├── curriculos/
│   └── dados/                # uma pasta por família de vagas
│       ├── v1/  v2/          # cada versão do currículo, nunca alterada depois de enviada
│       └── vagas/            # uma pasta por vaga: vaga.md, revisão e preparação
├── retrospectivas/           # uma por ciclo
└── tracker.csv
```

A Ana também mantém uma família `backend`, citada no tracker, que não aparece aqui para manter o exemplo curto.
