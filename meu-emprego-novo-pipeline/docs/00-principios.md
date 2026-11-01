# 00. Princípios

Antes de qualquer ferramenta, as regras que mantêm o processo honesto e sustentável.

## Objetivo

Reduzir o trabalho repetitivo da busca de emprego (adaptar currículo, preparar entrevista, acompanhar candidaturas) sem perder o controle sobre o que é dito em seu nome.

## Os sete princípios

### 1. Fonte única de verdade
Existe um arquivo, o `profile_truth.md`, que descreve sua carreira com o máximo de detalhe e precisão. Todo currículo, resumo de LinkedIn e resposta de entrevista é derivado dele. Se você muda de ideia sobre um fato, muda no perfil-mestre, não em cada documento.

### 2. Nunca inventar
O assistente pode reordenar, resumir, enfatizar e traduzir. Não pode acrescentar tecnologia, cargo, número ou certificação que não esteja na fonte. Se a vaga exige algo que você não fez, isso vira lacuna declarada.

### 3. Humano aprova
Nada é enviado sem você ler. Isso vale para currículo, mensagem a recrutador e resposta de formulário.

### 4. Regras duras para o que dá errado
Quando algo ruim acontece (golpe, empresa que você não quer, formulário que pede dado sensível), transforme em regra escrita. Regras escritas sobrevivem ao cansaço; boa vontade não.

### 5. Registrar para aprender
Sem rastreamento, você repete erros. Com um simples CSV, vê o que funciona.

### 6. Privacidade por padrão
Dados pessoais ficam em uma pasta privada. O que vai para o repositório público é método, não conteúdo pessoal.

### 7. Ritmo sustentável
Busca de emprego é maratona. Defina horários, pausas e um limite de candidaturas por dia. Qualidade antes de volume.

## Como aplicar os princípios no assistente de IA

Cole isto nas instruções do projeto (adapte ao seu caso):

```
Você me ajuda na busca de emprego.
- profile_truth.md é a única fonte de fatos sobre mim. Não afirme nada que não esteja nele.
- Nunca invente métricas, tecnologias, cargos, certificações ou datas.
- Quando a vaga exigir algo que não consta no perfil, registre como lacuna.
- Consulte vagas_excluidas.md antes de buscar ou recomendar vagas.
- Nunca preencha número de documento de identidade em formulários.
- Não envie nada em meu nome sem minha aprovação explícita.
```
