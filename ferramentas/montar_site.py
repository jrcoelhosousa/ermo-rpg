#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monta o site do SRD a partir do arquivo unico do livro.

Uso:
    python3 montar_site.py livro.md saida/ [NOME_DO_JOGO] [SUBTITULO]

Reconstroi o site inteiro do zero. Rode de novo sempre que o livro mudar:
o conteudo das paginas vem sempre do arquivo unico, nunca o contrario.
"""

import os
import re
import sys
import shutil
import unicodedata

NOME_ANTIGO = "GRIM"
SUBTITULO_ANTIGO = "*Gritty, Raw, Intentionally Makeshift*"

# (numero, titulo do H1 no livro, grupo do sumario)
GRUPOS = [
    ("Campanha",                "A moldura"),
    ("Resoluções",              "Os motores"),
    ("Desafios",                "Os motores"),
    ("Personagens",             "Os personagens"),
    ("Espaço e Tempo",          "Os personagens"),
    ("Exploração",              "Os personagens"),
    ("Equipamento",             "Os personagens"),
    ("Combate",                 "Os personagens"),
    ("Inventário",              "Os personagens"),
    ("Interação",               "Os personagens"),
    ("Magia",                   "Os personagens"),
    ("Expansões de Magia",      "Os personagens"),
    ("Encontros",               "O mundo"),
    ("Regiões e Hexágonos",     "O mundo"),
    ("Sítios",                  "O mundo"),
    ("Domínios",                "O mundo"),
    ("Acampamento",             "O mundo"),
    ("Inimigos",                "A oposição"),
    ("Vilões",                  "A oposição"),
    ("Bestiário",               "A oposição"),
    ("Cartões de Procedimento", "Na mesa"),
    ("As Folhas",               "Na mesa"),
    ("Uma Sessão Inteira",      "Na mesa"),
    ("Índice Remissivo",        "Na mesa"),
]

ORDEM_GRUPOS = ["A moldura", "Os motores", "Os personagens",
                "O mundo", "A oposição", "Na mesa"]


def slug(texto):
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def dividir_capitulos(texto):
    """Quebra o livro nos cabecalhos de nivel 1."""
    linhas = texto.split("\n")
    cortes = [i for i, l in enumerate(linhas) if l.startswith("# ")]
    blocos = []
    for n, inicio in enumerate(cortes):
        fim = cortes[n + 1] if n + 1 < len(cortes) else len(linhas)
        titulo = linhas[inicio][2:].strip()
        corpo = "\n".join(linhas[inicio + 1:fim]).strip("\n")
        blocos.append((titulo, corpo))
    return blocos


def limpar(corpo):
    """Tira separadores soltos no fim e espacos sobrando."""
    corpo = corpo.strip()
    while corpo.endswith("---"):
        corpo = corpo[:-3].rstrip()
    return corpo + "\n"


def frontmatter(campos):
    linhas = ["---"]
    for chave, valor in campos:
        if isinstance(valor, bool):
            linhas.append(f"{chave}: {'true' if valor else 'false'}")
        elif isinstance(valor, int):
            linhas.append(f"{chave}: {valor}")
        else:
            linhas.append(f'{chave}: "{valor}"')
    linhas.append("---")
    return "\n".join(linhas) + "\n\n"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    origem = sys.argv[1]
    destino = sys.argv[2]
    nome = sys.argv[3] if len(sys.argv) > 3 else "ERMO"
    subtitulo = sys.argv[4] if len(sys.argv) > 4 else "Escasso, Rude, Mal-acabado, Obstinado"

    texto = open(origem, encoding="utf-8").read()

    # renomeia o jogo
    texto = texto.replace(SUBTITULO_ANTIGO, f"*{subtitulo}*")
    texto = texto.replace(NOME_ANTIGO, nome)

    blocos = dividir_capitulos(texto)
    if not blocos:
        print("Nenhum capitulo (linha começando com '# ') encontrado.")
        sys.exit(1)

    abertura, capitulos = blocos[0], blocos[1:]

    esperados = [g[0] for g in GRUPOS]
    achados = [t for t, _ in capitulos]
    if achados != esperados:
        print("Aviso: os capitulos do livro nao batem com a tabela GRUPOS.")
        print("  no livro:", achados)
        print("  esperado:", esperados)
        print("Ajuste a lista GRUPOS no topo deste arquivo e rode de novo.\n")

    livro_dir = os.path.join(destino, "livro")
    os.makedirs(livro_dir, exist_ok=True)
    for f in os.listdir(livro_dir):
        if f.endswith(".md"):
            os.remove(os.path.join(livro_dir, f))

    # --- pagina inicial -------------------------------------------------
    corpo_abertura = limpar(abertura[1])

    # o Sumario do livro é texto puro; vira navegação de verdade no site.
    # site.baseurl é obrigatório aqui: sem ele os links quebram quando o site
    # mora em usuario.github.io/ermo/ em vez de num domínio próprio.
    for titulo, _ in capitulos:
        corpo_abertura = corpo_abertura.replace(
            f"**{titulo}**",
            f"[**{titulo}**]({{{{ site.baseurl }}}}/{slug(titulo)}/)"
        )
    inicio = frontmatter([
        ("title", "Início"),
        ("layout", "default"),
        ("nav_order", 1),
        ("permalink", "/"),
    ]) + corpo_abertura
    with open(os.path.join(destino, "index.md"), "w", encoding="utf-8") as fh:
        fh.write(inicio)

    # --- paginas de grupo -----------------------------------------------
    # O just-the-docs monta sozinho a lista de capitulos filhos. Escrever a
    # lista aqui a mao so criaria uma segunda copia para desatualizar.
    for i, grupo in enumerate(ORDEM_GRUPOS, start=2):
        pagina = frontmatter([
            ("title", grupo),
            ("layout", "default"),
            ("nav_order", i),
            ("has_children", True),
            ("permalink", f"/{slug(grupo)}/"),
        ])
        caminho = os.path.join(livro_dir, f"00-{slug(grupo)}.md")
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(pagina)

    # --- capitulos -------------------------------------------------------
    contador = {}
    escritos = []
    for n, (titulo, corpo) in enumerate(capitulos, start=1):
        grupo = dict(GRUPOS).get(titulo, "Na mesa")
        contador[grupo] = contador.get(grupo, 0) + 1
        s = slug(titulo)
        pagina = frontmatter([
            ("title", titulo),
            ("layout", "default"),
            ("parent", grupo),
            ("nav_order", contador[grupo]),
            ("permalink", f"/{s}/"),
        ]) + limpar(corpo)
        nome_arq = f"{n:02d}-{s}.md"
        with open(os.path.join(livro_dir, nome_arq), "w", encoding="utf-8") as fh:
            fh.write(pagina)
        escritos.append(nome_arq)

    print(f"index.md + {len(ORDEM_GRUPOS)} páginas de grupo + {len(escritos)} capítulos")
    print(f"nome aplicado: {nome}")


if __name__ == "__main__":
    main()
