from pathlib import Path
import re

ROOT = Path(".").resolve()

def extrair_versao(nome):
    m = re.search(r"-([\d\.]+)\.zip$", nome)
    return m.group(1) if m else None

def versao_key(ver):
    return [int(p) for p in ver.split(".")]

def zip_mais_recente(pasta: Path):
    zips = []
    for f in pasta.iterdir():
        if f.is_file() and f.suffix.lower() == ".zip":
            ver = extrair_versao(f.name)
            if ver:
                zips.append((ver, f))
    if not zips:
        return None
    return max(zips, key=lambda x: versao_key(x[0]))[1]

def coletar_zips_para_raiz():
    encontrados = {}
    for pasta in ROOT.iterdir():
        if pasta.is_dir() and not pasta.name.startswith("."):
            zip_ok = zip_mais_recente(pasta)
            if zip_ok:
                encontrados[zip_ok.name] = zip_ok
    return encontrados

def gerar_index(pasta: Path):
    linhas = [
        "<html>",
        "<body>",
        "<h1>Directory listing</h1>",
        "<hr/>",
        "<pre>"
    ]

    # link de retorno
    if pasta != ROOT:
        linhas.append('<a href="../index.html">..</a>')

    # pastas
    for item in sorted(pasta.iterdir(), key=lambda x: x.name.lower()):
        if item.is_dir() and not item.name.startswith("."):
            linhas.append(f'<a href="./{item.name}/index.html">{item.name}</a>')

    # zip local (se houver)
    zip_local = zip_mais_recente(pasta)
    if zip_local:
        linhas.append(f'<a href="./{zip_local.name}">{zip_local.name}</a>')

    linhas += ["</pre>", "</body>", "</html>"]
    (pasta / "index.html").write_text("\n".join(linhas), encoding="utf-8")

def gerar_index_raiz():
    linhas = [
        "<html>",
        "<body>",
        "<h1>Repository</h1>",
        "<hr/>",
        "<pre>"
    ]

    zips = coletar_zips_para_raiz()

    for nome in sorted(zips.keys()):
        zip_path = zips[nome]
        rel = zip_path.relative_to(ROOT)
        linhas.append(f'<a href="{rel.as_posix()}">{nome}</a>')

    linhas += ["</pre>", "</body>", "</html>"]
    (ROOT / "index.html").write_text("\n".join(linhas), encoding="utf-8")

def varrer():
    for pasta in ROOT.iterdir():
        if pasta.is_dir() and not pasta.name.startswith("."):
            gerar_index(pasta)
    gerar_index_raiz()

if __name__ == "__main__":
    varrer()
