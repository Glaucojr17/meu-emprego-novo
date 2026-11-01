# 03. Triagem

## Objetivo
Transformar uma lista longa em uma lista curta de vagas em que vale investir tempo.

## Entrada
Lista de vagas numerada (etapa 2) e `profile_truth.md`.

## Saída
Tabela de triagem:

| # | Vaga | Aderência | Por quê | Lacunas | Decisão |
|---|------|-----------|---------|---------|---------|
| 3 | Dev Backend Pleno, Empresa X | Alta | stack, domínio e senioridade batem | nenhuma crítica | candidatar |
| 7 | Eng. de Dados Sênior, Empresa Y | Média | pede Spark, perfil só estudou | Spark | decidir |
| 9 | Analista, Empresa Z | Baixa | senioridade abaixo, presencial em outra cidade | local | descartar |

## Critérios de aderência

- **Alta**: cobre os requisitos obrigatórios com evidência no perfil, modalidade e local aceitáveis.
- **Média**: cobre a maior parte; faltam itens que podem ser desejáveis ou aprendidos.
- **Baixa**: faltam requisitos obrigatórios, ou a vaga viola uma regra pessoal.

Peça ao assistente que cite, para cada vaga, **o trecho do perfil que sustenta a nota**. Sem evidência, a nota é opinião.

## Passo a passo
1. Cole a lista e o perfil no assistente.
2. Use o prompt de triagem.
3. Revise a tabela. Discorde quando fizer sentido; o assistente não conhece suas preferências tácitas.
4. Mova descartadas para a lista de exclusões, se o motivo for permanente.

## Sinais de alerta para descartar
- Descrição vaga demais, sem empresa identificada.
- Contato apenas por aplicativo de mensagens, sem canal corporativo.
- Promessa de remuneração muito acima do mercado sem requisitos.
- Pedido de pagamento ou de dados sensíveis antes de qualquer conversa.
- Processo que exija baixar e executar código fora de plataformas conhecidas.

## Erros comuns
- Candidatar-se a "média" sem ler a lacuna.
- Ignorar o ponto cultural (cliente final, horário, política de remoto).
- Reavaliar a mesma vaga várias vezes por falta de registro.

## Prompt
[`prompts/03-triagem.md`](../prompts/03-triagem.md)
