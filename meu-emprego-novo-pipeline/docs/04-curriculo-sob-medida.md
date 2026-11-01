# 04. Currículo sob medida: JSON → LaTeX → PDF

## Objetivo
Gerar, para cada família de vagas, um currículo que enfatize o que é relevante, mantendo tudo verdadeiro e com formatação consistente.

## Por que JSON?
- **Separa conteúdo de forma.** O assistente trabalha só o conteúdo; a formatação vem de um template fixo.
- **É validável.** Um script confere campos obrigatórios e detecta erros antes de gerar o PDF.
- **É comparável.** Você vê com `diff` o que mudou entre duas versões.

O formato segue a ideia do padrão aberto *JSON Resume* (seções `basics`, `work`, `education`, `skills`, `certificates`, `languages`, `projects`). Veja `templates/resume.json`.

## Entrada
- `profile_truth.md`
- Descrição da vaga em `vaga.md`

## Saída
Na pasta `privado/curriculos/<vaga>/`:
```
vaga.md
resume.json
curriculo.tex
curriculo.pdf
```

## Passo a passo

1. **Preparar a pasta**
   ```bash
   mkdir -p privado/curriculos/dev-backend-empresa-x
   # cole a descrição da vaga em vaga.md
   ```
2. **Gerar o JSON** com o prompt de [`prompts/04-curriculo-sob-medida.md`](../prompts/04-curriculo-sob-medida.md). As instruções-chave:
   - use somente fatos do perfil-mestre;
   - preserve **todos** os empregadores, cargos e datas reais;
   - reordene e reescreva os destaques para priorizar o que a vaga pede;
   - use as palavras da vaga **quando forem verdadeiras** para você (isso ajuda filtros automáticos);
   - não acrescente métricas.
3. **Validar**
   ```bash
   python3 scripts/validar_json.py privado/curriculos/dev-backend-empresa-x/resume.json
   ```
4. **Converter para LaTeX**
   ```bash
   python3 scripts/json_para_latex.py \
     privado/curriculos/dev-backend-empresa-x/resume.json \
     privado/curriculos/dev-backend-empresa-x/curriculo.tex
   ```
5. **Compilar**
   ```bash
   pdflatex -output-directory privado/curriculos/dev-backend-empresa-x \
     privado/curriculos/dev-backend-empresa-x/curriculo.tex
   ```
6. **Ler o PDF inteiro**: nomes, datas, ortografia, número de páginas, caracteres especiais.

## Boas práticas

- **Uma versão por família de vagas.** Não precisa de 60 versões; precisa de 4 a 6 bem feitas e ajustes pontuais.
- **Nomeie as pastas pelo cargo**, não pela empresa, para reaproveitar.
- **Priorize**: resumo de 3 a 4 linhas, 3 a 5 destaques por empresa recente, menos nas antigas.
- **Número de páginas**: 2 páginas para carreiras longas é aceitável; mais que isso raramente é lido.
- **Idioma**: gere versão em inglês quando a vaga for internacional ou a descrição estiver em inglês, e revise a tradução.
- **Certificações**: informe a situação real (válida, expirada, em renovação).

## Erros comuns
- Pedir "deixe mais impressionante" sem restrição: o assistente tende a inventar.
- Esquecer de remover dados que não devem ir (por exemplo, links pessoais não profissionais).
- Caracteres especiais quebrando o LaTeX (o script `json_para_latex.py` faz o escape, mas confira).
- Enviar PDF sem abrir.

## Conferência final (checklist)
- [ ] Todos os empregadores aparecem com datas corretas
- [ ] Nenhum número sem origem no perfil-mestre
- [ ] Palavras-chave da vaga presentes **apenas** quando verdadeiras
- [ ] Certificações com situação correta
- [ ] Contato correto e sem dados desnecessários
- [ ] PDF aberto e lido de ponta a ponta
