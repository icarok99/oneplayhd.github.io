from pathlib import Path
import re

# =============================
# Utils
# =============================

def extrair_versao(nome: str):
    m = re.search(r"One\.repo-(\d+(?:\.\d+)*)\.zip", nome)
    if not m:
        return ()
    return tuple(map(int, m.group(1).split(".")))


def pasta_tem_zip_recursivo(pasta: Path) -> bool:
    return any(p.suffix.lower() == ".zip" for p in pasta.rglob("*.zip"))


# =============================
# Repositório mais recente
# =============================

def encontrar_repos_mais_recentes(raiz: Path) -> list[Path]:
    encontrados = []

    for item in raiz.rglob("One.repo-*.zip"):
        versao = extrair_versao(item.name)
        if versao:
            encontrados.append((versao, item))

    if not encontrados:
        return []

    maior = max(v for v, _ in encontrados)
    return [p for v, p in encontrados if v == maior]


# =============================
# Index handling
# =============================

def gerar_ou_remover_index(pasta: Path, raiz: Path, repos_recentes: list[Path]):
    index = pasta / "index.html"
    tem_zip = pasta_tem_zip_recursivo(pasta)

    # ❌ subpasta sem zip → remove index
    if pasta != raiz and not tem_zip:
        if index.exists():
            index.unlink()
            print(f"🧹 removido: {index}")
        return

    # ❌ raiz sem zip nenhum → remove index
    if pasta == raiz and not repos_recentes:
        if index.exists():
            index.unlink()
            print(f"🧹 removido: {index}")
        return

    # ✅ cria / recria index
    linhas = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        "<title>Directory listing</title>",
        "</head>",
        "<body>",
        "<h1>Directory listing</h1>",
        "<hr/>",
        "<pre>",
    ]

    if pasta != raiz:
        linhas.append('<a href="../index.html">..</a>')

    for item in sorted(pasta.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        if item.name.startswith(".") or item.name == "index.html":
            continue

        if item.is_dir():
            # lista só se houver zip dentro
            if pasta_tem_zip_recursivo(item):
                linhas.append(f'<a href="./{item.name}/index.html">{item.name}/</a>')
        elif item.is_file() and item.suffix.lower() == ".zip":
            linhas.append(f'<a href="./{item.name}">{item.name}</a>')

    linhas.extend([
        "</pre>",
        "</body>",
        "</html>",
    ])

    # 🔥 tabela técnica FORA do HTML (apenas na raiz)
    if pasta == raiz and repos_recentes:
        linhas.append("")
        linhas.append('<div id="Repositorio-KODI" style="display:none">')
        linhas.append("<table>")
        for repo in repos_recentes:
            rel = repo.relative_to(raiz).as_posix()
            linhas.append(f'<tr><td><a href="{rel}">{rel}</a></td></tr>')
        linhas.append("</table>")
        linhas.append("</div>")

    index.write_text("\n".join(linhas), encoding="utf-8")
    print(f"✔ index atualizado: {pasta}")


# =============================
# Varredura bottom-up (SEM raiz)
# =============================

def varrer_bottom_up(pasta: Path, raiz: Path, repos_recentes: list[Path]):
    for sub in pasta.iterdir():
        if sub.is_dir() and not sub.name.startswith("."):
            varrer_bottom_up(sub, raiz, repos_recentes)

    gerar_ou_remover_index(pasta, raiz, repos_recentes)


# =============================
# Main
# =============================

if __name__ == "__main__":
    raiz = Path(".")

    # calcula versão mais recente
    repos_recentes = encontrar_repos_mais_recentes(raiz)

    # 🔥 percorre APENAS subpastas (raiz não entra aqui)
    for sub in raiz.iterdir():
        if sub.is_dir() and not sub.name.startswith("."):
            varrer_bottom_up(sub, raiz, repos_recentes)

    # 🔥 gera raiz UMA ÚNICA VEZ
    gerar_ou_remover_index(raiz, raiz, repos_recentes)
