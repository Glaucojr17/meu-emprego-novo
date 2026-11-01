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
Uma pasta por família de vagas, com as versões do currículo e uma pasta para cada vaga:
```
privado/curriculos/dados/
├── v1/
│   ├── resume.json
│   ├── curriculo.tex
│   └── curriculo.pdf
└── vagas/
    └── 2026-09-10-empresa-delta/
        ├── vaga.md
        ├── coverage_review.md
        └── interview_prep.md
```

## Passo a passo

Estes passos criam a primeira versão de uma família.

1. **Preparar as pastas**
   ```bash
   mkdir -p privado/curriculos/dados/v1 privado/curriculos/dados/vagas/2026-09-10-empresa-delta
   # cole a descrição da vaga em vaga.md, na pasta da vaga
   ```
2. **Gerar o JSON** com o prompt de [`prompts/04-curriculo-sob-medida.md`](../prompts/04-curriculo-sob-medida.md). As instruções-chave:
   - use somente fatos do perfil-mestre;
   - preserve **todos** os empregadores, cargos e datas reais;
   - reordene e reescreva os destaques para priorizar o que a vaga pede;
   - use as palavras da vaga **quando forem verdadeiras** para você (isso ajuda filtros automáticos);
   - não acrescente métricas.

   Salve só o JSON em `resume.json`: do primeiro `{` ao último `}`, sem bloco de código e sem comentários.
3. **Validar**
   ```bash
   python3 scripts/validar_json.py privado/curriculos/dados/v1/resume.json
   ```
4. **Converter para LaTeX**
   ```bash
   python3 scripts/json_para_latex.py \
     privado/curriculos/dados/v1/resume.json \
     privado/curriculos/dados/v1/curriculo.tex
   ```
5. **Compilar**
   ```bash
   pdflatex -output-directory privado/curriculos/dados/v1 \
     privado/curriculos/dados/v1/curriculo.tex
   ```
6. **Ler o PDF inteiro**: nomes, datas, ortografia, número de páginas, caracteres especiais.

## Quando chegar a próxima vaga

Para outra vaga da mesma família, parta da versão mais recente:

1. Crie `vagas/<data-empresa>/` e salve nela o `vaga.md`.
2. Rode a [revisão de cobertura](05-coverage-review.md) com a versão mais recente.
3. Decida:
   - **Cobertura boa:** envie a mesma versão.
   - **Fato verdadeiro fora de lugar ou faltando:** crie `v2/` com o prompt [`04b-ajustar-curriculo.md`](../prompts/04b-ajustar-curriculo.md), repita os passos 3 a 6 e refaça a revisão. Se o fato não estiver no perfil-mestre, acrescente-o lá primeiro.
   - **Lacuna obrigatória:** decida como na revisão de cobertura. Não ajuste o currículo para disfarçá-la.
   - **Vaga de outro tipo:** crie uma nova família.
4. Registre no tracker a versão enviada, como `dados-v2`.

**Nunca altere uma versão já enviada.** Toda mudança vira uma versão nova; assim você sabe o que cada empresa recebeu.

Veja a [Ana fazendo isso no segundo ciclo](../exemplo/README.md#o-segundo-ciclo).

## Boas práticas

- **De 4 a 6 famílias no máximo.** Não precisa de 60 currículos; precisa de poucas bases bem feitas e ajustes pontuais.
- **Nomeie cada família pelo tipo de vaga**, não pela empresa, para reaproveitar.
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
