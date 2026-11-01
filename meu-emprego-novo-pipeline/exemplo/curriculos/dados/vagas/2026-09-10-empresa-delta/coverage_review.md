# Revisão de cobertura (EXEMPLO FICTÍCIO)

**Alvo:** Engenheiro(a) de Dados Pleno, Empresa Delta.
**Versão avaliada:** `dados-v1`.
**Fontes:** `perfil/profile_truth.md` (prioridade), `curriculos/dados/v1/resume.json` e `vaga.md`.

## Preservado
Dois empregadores, cargos e datas reais mantidos. Quatro destaques na empresa atual e dois na anterior, todos presentes no perfil-mestre. Nenhuma métrica nova.

## Cobertura forte
| Requisito | Currículo | Evidência no perfil |
|-----------|-----------|---------------------|
| Python avançado | Destaques de FastAPI/Django | Empresa Beta e Gama |
| SQL | Relatórios em MySQL; PostgreSQL | Empresa Gama e Beta |
| CI/CD, Docker (desejável) | Pipelines de deploy | Empresa Beta |

## Cobertura parcial
- **Pipelines de dados (ETL/ELT):** relatórios SQL e integrações por filas sustentam a base, mas não há pipeline de dados analítico em produção.
- **Inglês para leitura técnica:** consta como "leitura técnica fluente".

## Lacunas não inventadas
- **Airflow em produção** (obrigatório): apenas estudo.
- **Experiência com nuvem em produção** (obrigatório): apenas certificação fundamental e projetos pessoais.
- **Spark** (desejável): apenas estudo.

## Inconsistências encontradas
Nenhuma. Todos os números do currículo constam no perfil-mestre com origem `[medido]`.

## Decisão sugerida
Duas lacunas obrigatórias (Airflow e nuvem em produção). Candidatura possível se Ana aceitar discutir abertamente que está em transição e tem projeto prático de Airflow em andamento (se existir; hoje não consta no perfil).

*Esta revisão não afirma que todos os requisitos obrigatórios são atendidos.*
