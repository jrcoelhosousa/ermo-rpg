# ERMO — repositório do SRD

O livro inteiro, em texto aberto, servido como site de consulta.

Ele é um site Jekyll com o tema [just-the-docs](https://just-the-docs.com), publicado pelo GitHub Pages. É a mesma receita do site do Cairn, que é o que você pediu.

## A regra que segura tudo

**O livro mora em `ferramentas/livro-fonte.md`. As páginas de `livro/` são geradas.**

Você edita o arquivo único e roda o montador. Nunca o contrário. Se você editar uma página em `livro/` direto, a próxima montagem apaga a edição.

```bash
python3 ferramentas/montar_site.py ferramentas/livro-fonte.md . ERMO "Escasso, Rude, Mal-acabado, Obstinado"
```

Os dois últimos argumentos são o nome do jogo e o subtítulo, e são opcionais.

**O `livro-fonte.md` ainda diz GRIM de propósito.** O nome é aplicado na hora de montar, não está gravado no texto. Enquanto você estiver decidindo, testar outro nome é uma linha:

```bash
python3 ferramentas/montar_site.py ferramentas/livro-fonte.md . TORVO "Duro, seco, sem promessa"
```

Quando o nome estiver fechado, rode um `sed -i 's/GRIM/ERMO/g' ferramentas/livro-fonte.md` e ajuste o subtítulo na segunda linha do arquivo. A partir daí o argumento vira só formalidade.

## Publicar pela primeira vez

1. Crie um repositório público no GitHub chamado `ermo` e mande estes arquivos para o branch `main`.
2. Em **Settings → Pages**, mude *Source* para **GitHub Actions**.
3. Em `_config.yml` e no `CNAME`, troque `SEU-USUARIO`, `SEU NOME` e `ermo.com.br` pelos seus.
4. No painel do seu domínio, aponte para o GitHub Pages:
   - `CNAME` de `www` para `SEU-USUARIO.github.io`
   - registros `A` do domínio raiz para `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
5. Volte em **Settings → Pages**, escreva o domínio em *Custom domain* e marque *Enforce HTTPS*.

Sem domínio próprio, o site já vive em `SEU-USUARIO.github.io/ermo/` — apague o `CNAME` e tire a linha `url:` do `_config.yml`.

Depois disso, todo `git push` no `main` republica o site sozinho.

## Rodar na sua máquina antes de publicar

```bash
bundle install
bundle exec jekyll serve --livereload
```

E abra `http://localhost:4000`. Precisa de Ruby 3.x instalado.

## O que é cada coisa

| Caminho | O que é |
|---|---|
| `ferramentas/livro-fonte.md` | O livro. A única fonte de verdade. |
| `ferramentas/montar_site.py` | Quebra o livro em capítulos e escreve o `front matter`. |
| `index.md` | Página inicial: a abertura e o Sumário, gerados. |
| `livro/` | Um arquivo por capítulo. Gerado. |
| `_config.yml` | Título, domínio, busca, rodapé, links. |
| `_sass/color_schemes/escuro.scss` | A paleta. |
| `_sass/custom/custom.scss` | Tipografia, tabelas, impressão. |
| `.github/workflows/pages.yml` | O que publica a cada push. |

## Se você mexer nos capítulos do livro

O montador tem uma lista chamada `GRUPOS` no topo do arquivo, que diz em que seção do menu cada capítulo entra. Se você criar, apagar ou renomear um capítulo (uma linha começando com `# `), ele avisa que a lista não bate e diz o que mudou. Ajuste a lista e rode de novo.

## Licença

O texto está sob [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.pt-br). Qualquer pessoa pode copiar, traduzir, remixar e vender o resultado, desde que dê o crédito e mantenha a mesma licença. É a licença do Cairn, e é ela que faz um SRD virar um SRD em vez de um PDF de graça.
