# Todas as leis do Brasil em Markdown

Repositório: https://github.com/ctresb/leis (João Davi, scripts MIT; os textos
legais são de domínio público pela Lei 9.610/98, art. 8º, I).

Tem cerca de **1,35 milhão de arquivos**, vários GB: um Markdown por norma
(federal, estaduais, municipais, reguladores, jurisprudência, tratados e
Constituição). Por isso ele **não** foi copiado para cá. Baixe só a parte que
precisar:

```bash
./scripts/leis.sh federal/leis-ordinarias   # baixa em ~/leis; a Constituição já vem junto
./scripts/leis.sh federal/decretos                          # adiciona mais pastas depois
```

Depois, no Claude Code, dentro de `~/leis`:

> Procure em federal/leis-ordinarias o que a lei diz sobre prazo de
> arrependimento em compras online e cite o artigo e o arquivo.

Atenção: os textos foram convertidos automaticamente, alguns com OCR, e **não
substituem o Diário Oficial**. Confira o link da fonte oficial que vem no
cabeçalho de cada arquivo antes de usar em algo sério.
