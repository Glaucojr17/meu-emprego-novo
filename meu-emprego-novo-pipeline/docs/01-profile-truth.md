# 01. Perfil-mestre (`profile_truth.md`)

O arquivo mais importante do pipeline. Tudo nasce dele.

## Objetivo
Ter, em um só lugar, a versão **longa, completa e verdadeira** da sua carreira, da qual saem versões curtas e direcionadas.

## Entrada
- Currículos antigos, perfil de LinkedIn, certificados, memória da sua trajetória.
- Tempo para lembrar de projetos, resultados e contexto (reserve 1 a 2 horas).

## Saída
`privado/perfil/profile_truth.md`, com seções:

1. **Identidade profissional**: como você se define, senioridade, áreas.
2. **Contato**: só o que pode aparecer no currículo. O assistente não usa dados de contato de outro lugar.
3. **Experiência por empresa**: cargo, período, contexto, responsabilidades, tecnologias, resultados.
4. **Formação e certificações**: com situação (concluída, em andamento, expirada).
5. **Competências**: separe *domina*, *usa com frequência* e *estudou*.
6. **Idiomas**: nível real.
7. **Lacunas conhecidas**: o que você não fez.
8. **Regras de comunicação**: o que nunca deve aparecer (dados pessoais, informações confidenciais de ex-empregadores).
9. **Adendos**: detalhes lembrados depois.

## Passo a passo

1. Copie `templates/profile_truth.md` para `privado/perfil/`.
2. Para cada empresa, responda: *que problema eu resolvi? como? com quê? qual foi o resultado?*
3. Marque a origem de cada número:
   - `[medido]`: existe relatório, painel ou documento que comprove;
   - `[estimado]`: você tem boa noção, mas sem prova;
   - `[sem número]`: resultado qualitativo.
   Só `[medido]` entra em currículo sem ressalvas.
4. Escreva as lacunas sem rodeios.
5. Anexe o arquivo ao projeto do assistente.
6. Use o [prompt de entrevista](../prompts/01-perfil-mestre.md) para o assistente **fazer perguntas** e encontrar detalhes esquecidos. Responda apenas o que for verdade.

## Erros comuns
- **Copiar o currículo antigo como se fosse a verdade.** Currículos antigos já são versões resumidas e podem ter números sem lastro.
- **Misturar o que você fez com o que o time fez.** Use "liderei", "participei", "apoiei" com precisão.
- **Esquecer certificações expiradas.** Registre a data de expiração; um currículo que as apresenta como válidas se torna problema na entrevista.
- **Apagar as lacunas.** São elas que protegem você de respostas inventadas.

## Dica: complemento incremental
Ao longo do processo você vai lembrar de detalhes novos. Registre-os com a data na seção "Adendos" e, periodicamente, consolide nas seções principais.

## Exemplo
Veja [`exemplo/perfil/profile_truth.md`](../exemplo/perfil/profile_truth.md).
