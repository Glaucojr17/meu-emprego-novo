# 07. Rastreamento de candidaturas

## Objetivo
Saber, a qualquer momento: onde me candidatei, com qual currículo, o que respondeu, qual o próximo passo.

## Entrada
Cada candidatura enviada e cada resposta recebida.

## Saída
`privado/tracker.csv` (ou planilha) com as colunas:

| coluna | exemplo |
|--------|---------|
| data | 2026-09-12 |
| empresa | Empresa Alfa |
| vaga | Dev Backend Pleno |
| fonte | LinkedIn |
| tipo | simplificada / externa |
| link | https://... |
| curriculo | dev-backend-v2 |
| status | enviada / triagem / entrevista / teste / oferta / recusada / descartada |
| proximo_passo | entrevista RH em 20/09 |
| observacoes | cliente final: confirmar |

## Passo a passo
1. Copie `templates/tracker.csv` para `privado/tracker.csv`.
2. Registre **logo após** cada envio. Se deixar para depois, esquece.
3. Ao receber resposta, atualize `status`, `proximo_passo` e `observacoes`.
4. Peça ao assistente um resumo semanal: quantas enviadas, quantas respostas, quais fontes e versões de currículo funcionaram.

## Registre também
- **Entrevistas marcadas**: data, hora, link, nome do contato (apenas no arquivo privado).
- **Motivos de recusa de sua parte**: ajudam a refinar `vagas_excluidas.md`.
- **Sinais de golpe**: para consultar depois.

## Métricas simples que vale olhar
- Taxa de resposta por versão de currículo.
- Taxa de resposta por fonte.
- Tempo médio entre envio e primeira resposta.
- Quantas vagas "alta aderência" geraram entrevista.

## Erros comuns
- Planilha desatualizada.
- Candidatar-se duas vezes à mesma vaga com currículos diferentes.
- Não registrar a versão do currículo enviada: depois você não sabe o que prometeu.

## Privacidade
Nomes de recrutadores, e-mails e telefones **ficam só no arquivo privado**. Nunca publique.
