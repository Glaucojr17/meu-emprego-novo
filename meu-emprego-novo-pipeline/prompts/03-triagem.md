# Prompt: triagem de vagas

```
Avalie as vagas da lista abaixo contra profile_truth.md.

Para cada vaga, devolva uma linha de tabela com:
número | título/empresa | aderência (alta/média/baixa) | evidência no perfil (cite o trecho) | lacunas obrigatórias | recomendação (candidatar / decidir / descartar)

Regras:
- Aderência "alta" só se os requisitos obrigatórios tiverem evidência no perfil.
- Se faltar evidência, escreva "sem evidência"; não suponha.
- Marque sinais de golpe (domínio de e-mail estranho, pedido de documento ou pagamento, teste que exige baixar código).
- Respeite vagas_excluidas.md.

Lista:
[cole aqui]
```
