from pathlib import Path

def gerar_index_em_pasta(pasta: Path):
    itens = sorted(
        pasta.iterdir(),
        key=lambda x: (x.is_file(), x.name.lower())
    )

    linhas = []
    linhas.append("<html>")
    linhas.append("<body>")
    linhas.append("<h1>Directory listing</h1>")
    linhas.append("<hr/>")
    linhas.append("<pre>")

    # link para pasta pai
    if pasta.parent != pasta:
        linhas.append('<a href="../index.html">..</a>')

    for item in itens:
        if item.name.startswith("."):
            continue

        if item.name == "index.html":
            continue

        if item.is_dir():
            linhas.append(
                f'<a href="./{item.name}\\index.html">{item.name}</a>'
            )

        elif item.is_file() and item.suffix.lower() == ".zip":
            linhas.append(
                f'<a href="./{item.name}">{item.name}</a>'
            )

    linhas.append("</pre>")
    linhas.append("</body>")
    linhas.append("</html>")

    (pasta / "index.html").write_text(
        "\n".join(linhas),
        encoding="utf-8"
    )

    print(f"✔ index gerado em: {pasta}")

def varrer_recursivo(raiz: Path):
    gerar_index_em_pasta(raiz)

    for item in raiz.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            varrer_recursivo(item)

if __name__ == "__main__":
    raiz = Path(".")
    varrer_recursivo(raiz)
