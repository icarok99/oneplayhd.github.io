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
        if f.is_file() and f.suffix == ".zip":
            ver = extrair_versao(f.name)
            if ver:
                zips.append((ver, f))
    if not zips:
        return None
    return max(zips, key=lambda x: versao_key(x[0]))[1]

# 🔹 MODO HUMANO (SUBPASTAS)
def gerar_index_pasta(pasta: Path):
    zip_local = zip_mais_recente(pasta)
    if not zip_local:
        return

    linhas = [
        "<html><body>",
        f"<h1>{pasta.name}</h1>",
        "<hr><pre>",
        '<a href="../index.html">..</a>',
        f'<a href="{zip_local.name}">{zip_local.name}</a>',
        "</pre></body></html>"
    ]

    (pasta / "index.html").write_text("\n".join(linhas), encoding="utf-8")

# 🔹 MODO KODI (RAIZ)
def gerar_index_kodi():
    linhas = [
        "<html><body>",
        "<h1>Kodi Repository</h1>",
        "<hr><pre>"
    ]

    for pasta in sorted(ROOT.iterdir(), key=lambda x: x.name.lower()):
        if not pasta.is_dir() or pasta.name.startswith("."):
            continue

        zip_ok = zip_mais_recente(pasta)
        if zip_ok:
            rel = zip_ok.relative_to(ROOT).as_posix()
            linhas.append(f'<a href="{rel}">{zip_ok.name}</a>')

    linhas += ["</pre></body></html>"]
    (ROOT / "index.html").write_text("\n".join(linhas), encoding="utf-8")

def main():
    for pasta in ROOT.iterdir():
        if pasta.is_dir() and not pasta.name.startswith("."):
            gerar_index_pasta(pasta)
    gerar_index_kodi()

if __name__ == "__main__":
    main()
