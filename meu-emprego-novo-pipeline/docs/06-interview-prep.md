# 06. Preparação de entrevista (`interview_prep.md`)

## Objetivo
Entrar na entrevista tendo ensaiado as perguntas prováveis com **histórias verdadeiras** suas.

## Entrada
`vaga.md`, `resume.json`, `coverage_review.md`, `profile_truth.md`.

## Saída
`interview_prep.md`, na pasta da vaga, com:

1. **Análise da vaga**: o que a empresa quer e os três critérios que decidem a entrevista.
2. **Perguntas prováveis** (técnicas, comportamentais, situacionais, motivação) com:
   - por que perguntam;
   - resposta sugerida em estrutura STAR (Situação, Tarefa, Ação, Resultado);
   - pontos de apoio.
3. **Mensagens-chave** que você precisa transmitir.
4. **Pontos fracos a antecipar**, usando as lacunas do `coverage_review`.
5. **Perguntas para fazer** ao entrevistador.
6. **Checklist logístico**: ambiente, câmera, documentos, pesquisa sobre a empresa.
7. **Negociação**: como responder sobre pretensão salarial.

## Regra principal
As respostas são **rascunhos**. Duas verificações obrigatórias:

1. **Cada fato e número deve existir no perfil-mestre.** Se o rascunho trouxer um número que você não reconhece, apague.
2. **Reescreva com suas palavras.** Em voz alta. Texto de IA decorado soa artificial e se desfaz na primeira pergunta de follow-up.

## Passo a passo
1. Rode o prompt de [`prompts/06-interview-prep.md`](../prompts/06-interview-prep.md).
2. Marque no arquivo toda afirmação duvidosa e verifique no perfil-mestre.
3. Escolha de 5 a 6 histórias reais suas e adapte cada uma a mais de uma pergunta.
4. Ensaie em voz alta, de preferência gravando.
5. Para lacunas: prepare uma resposta honesta no formato *"não tenho experiência direta com X; o mais próximo que fiz foi Y; estou estudando Z"*.

## Sobre salário
- Pesquise faixa de mercado em fontes públicas antes da conversa.
- Prefira dar uma faixa e discutir o pacote total (benefícios, modalidade, desenvolvimento).
- Os valores que o assistente sugerir são estimativas genéricas, não dados confiáveis. **Não publique nem confie cegamente neles.**

## Sobre testes técnicos
Veja [docs/08-golpes-e-seguranca.md](08-golpes-e-seguranca.md): teste legítimo ocorre em plataforma conhecida; não exige baixar e executar nada no seu computador.

## Erros comuns
- Decorar respostas.
- Usar o mesmo exemplo para tudo.
- Não pesquisar a empresa.
- Não ter perguntas para fazer.

## Exemplo
[Preparação da Ana para a vaga da Delta](../exemplo/curriculos/dados/vagas/2026-09-10-empresa-delta/interview_prep.md)
