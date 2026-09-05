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

# Os capitulos do livro, na ordem. Serve so para conferir que o arquivo
# fonte nao mudou de forma sem o montador saber.
CAPITULOS = [
    "Campanha",
    "Resoluções",
    "Desafios",
    "Personagens",
    "Espaço e Tempo",
    "Exploração",
    "Equipamento",
    "Combate",
    "Inventário",
    "Interação",
    "Magia",
    "Expansões de Magia",
    "Encontros",
    "Regiões e Hexágonos",
    "Sítios",
    "Domínios",
    "Acampamento",
    "Inimigos",
    "Vilões",
    "Bestiário",
    "Cartões de Procedimento",
    "As Folhas",
    "Uma Sessão Inteira",
    "Índice Remissivo",
]




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

    esperados = CAPITULOS
    achados = [t for t, _ in capitulos]
    if achados != esperados:
        print("Aviso: os capitulos do livro nao batem com a lista CAPITULOS.")
        print("  no livro:", achados)
        print("  esperado:", esperados)
        print("Ajuste a lista CAPITULOS no topo deste arquivo e rode de novo.\n")

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

    # --- capitulos -------------------------------------------------------
    escritos = []
    for n, (titulo, corpo) in enumerate(capitulos, start=1):
        s = slug(titulo)
        # nav_order 1 é o Início; os capítulos seguem na ordem do livro
        pagina = frontmatter([
            ("title", titulo),
            ("layout", "default"),
            ("nav_order", n + 1),
            ("permalink", f"/{s}/"),
        ]) + limpar(corpo)
        nome_arq = f"{n:02d}-{s}.md"
        with open(os.path.join(livro_dir, nome_arq), "w", encoding="utf-8") as fh:
            fh.write(pagina)
        escritos.append(nome_arq)

    print(f"index.md + {len(escritos)} capítulos, todos no primeiro nível")
    print(f"nome aplicado: {nome}")


if __name__ == "__main__":
    main()
