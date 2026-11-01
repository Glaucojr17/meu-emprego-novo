# Revisão de cobertura (EXEMPLO FICTÍCIO)

**Alvo:** Engenheiro(a) de Dados Júnior/Pleno, Empresa Teta.
**Versão avaliada:** primeiro a `dados-v1`, depois a `dados-v2`.
**Fontes:** `perfil/profile_truth.md` (prioridade), `curriculos/dados/v2/resume.json` e `vaga.md`.

## Resultado com a `dados-v1`
Os relatórios em SQL, centrais para esta vaga, ficavam só no último destaque da empresa mais antiga, e as rotinas agendadas não apareciam. Por isso a Ana criou a `dados-v2` com o prompt de ajuste.

## Preservado na `dados-v2`
Dois empregadores, cargos e datas reais mantidos. Um destaque novo, baseado nos adendos do perfil-mestre. Nenhuma métrica nova.

## Cobertura forte
| Requisito | Currículo | Evidência no perfil |
|-----------|-----------|---------------------|
| Python e SQL | Destaques de FastAPI, Django e relatórios | Empresa Beta e Gama |
| Relatórios para áreas de negócio | Relatórios de vendas para a área comercial | Empresa Gama |
| Rotinas agendadas | Rotinas SQL agendadas para os relatórios | Adendo de 2026-09-21 |
| PostgreSQL, Docker e CI/CD (desejáveis) | APIs e automação de deploy | Empresa Beta |

## Cobertura parcial
Nenhuma.

## Lacunas não inventadas
- **Airflow** (desejável): apenas estudo, como consta na seção "Em estudo" do currículo.

## Inconsistências encontradas
Nenhuma. Os números do currículo constam no perfil-mestre com origem `[medido]`.

## Decisão sugerida
Candidatar-se com a `dados-v2`. Nenhum requisito obrigatório está em aberto.

*Esta revisão não afirma que todos os requisitos obrigatórios são atendidos.*
