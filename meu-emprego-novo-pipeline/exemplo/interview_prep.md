# Preparação de entrevista (EXEMPLO FICTÍCIO, versão resumida)

**Vaga:** Engenheiro(a) de Dados Pleno, Empresa Delta.

## 1. O que decide a entrevista
1. Solidez em Python e SQL.
2. Raciocínio de pipeline de dados (confiabilidade, reprocessamento, qualidade).
3. Honestidade e plano de aprendizado nas lacunas (Airflow e nuvem).

## 2. Perguntas prováveis (amostra)

### Técnica: "Como você garantiria que um pipeline pode ser reexecutado sem duplicar dados?"
- **Por que perguntam:** testa idempotência, um conceito central em engenharia de dados.
- **Rascunho de resposta:** descrever chaves naturais, escrita com `upsert`/substituição de partição e registro de execuções. Usar como apoio a experiência com integrações por fila na Empresa Beta (reprocessamento de mensagens).
- **Pontos de apoio:** idempotência, particionamento, controle de execução.
- **Verificar no perfil:** a experiência com filas existe; não afirmar experiência com orquestrador.

### Comportamental (STAR): "Conte um caso em que você melhorou algo de forma mensurável."
- **Situação:** endpoint crítico lento na Empresa Beta.
- **Tarefa:** reduzir o tempo de resposta.
- **Ação:** (descrever, com suas palavras, o que realmente foi feito).
- **Resultado:** de 1,8 s para 0,6 s, medido em painel de APM.

### Lacuna: "Você já usou Airflow em produção?"
- **Resposta honesta:** "Não em produção. Estudei [o que realmente estudou] e o mais próximo que fiz foi [exemplo real]. Quero aprofundar e tenho [plano real]."
- **Evitar:** insinuar experiência que não existe.

## 3. Mensagens-chave
1. Python e SQL sólidos, com entrega comprovada.
2. Entrega automatizada (CI/CD) e preocupação com confiabilidade.
3. Transição consciente, com estudo em andamento.

## 4. Perguntas para fazer
1. Como é o ciclo de vida de um pipeline aqui, do desenvolvimento ao monitoramento?
2. Como vocês tratam qualidade de dados e reprocessamento?
3. Qual o plano de onboarding para quem ainda não domina o orquestrador de vocês?

## 5. Checklist
- [ ] Reescrever todas as respostas com minhas palavras e ensaiar em voz alta
- [ ] Pesquisar a empresa e o produto
- [ ] Testar câmera e áudio
- [ ] Pesquisar faixa salarial em fontes públicas
