import os
import re
import json
import urllib.request

USERNAME = os.environ.get("GH_USERNAME", "Caua031")
TOKEN = os.environ.get("GH_TOKEN")
MAX_REPOS = 6
MAX_LANGS_PER_REPO = 4
MIN_LANG_SHARE = 0.08  # ignora linguagem com menos de 8% do código do repo

headers = {"Accept": "application/vnd.github+json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

def get_json(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

url = f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=100"
repos = get_json(url)

repos = [r for r in repos if not r.get("fork") and r["name"].lower() != USERNAME.lower()]
repos = repos[:MAX_REPOS]

LANG_ICON = {
    "Python": "python", "JavaScript": "javascript", "TypeScript": "typescript",
    "HTML": "html", "CSS": "css", "C": "c", "C++": "cpp", "C#": "csharp",
    "Java": "java", "PHP": "php", "Go": "go", "Rust": "rust", "Ruby": "ruby",
    "Swift": "swift", "Kotlin": "kotlin", "Dart": "dart", "Shell": "bash",
    "Vue": "vue", "SCSS": "sass", "Dockerfile": "docker",
    "Jupyter Notebook": "python", "PLpgSQL": "postgres", "PLSQL": "oracle",
}

def top_languages(repo_name):
    try:
        lang_bytes = get_json(f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages")
    except Exception:
        return []
    total = sum(lang_bytes.values()) or 1
    items = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)
    picked = [name for name, b in items if b / total >= MIN_LANG_SHARE][:MAX_LANGS_PER_REPO]
    if not picked and items:
        picked = [items[0][0]]
    return picked

def card(r):
    langs = top_languages(r["name"])
    icons = [LANG_ICON[l] for l in langs if l in LANG_ICON]
    icon_html = f'<img src="https://skillicons.dev/icons?i={",".join(icons)}" height="24"/>\n\n' if icons else ""
    desc = (r.get("description") or "Sem descrição ainda.").strip()
    return (
        '<td width="50%" valign="top">\n\n'
        f'### {r["name"]}\n'
        f'{desc}\n\n'
        f'{icon_html}'
        f'⭐ {r["stargazers_count"]}\n\n'
        f'[Ver repositório](https://github.com/{USERNAME}/{r["name"]})\n\n'
        '</td>'
    )

cards = [card(r) for r in repos]
if not cards:
    table = "_nenhum repositório público encontrado ainda._"
else:
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")
    table = '<table width="100%">\n' + "\n".join(rows) + "\n</table>"

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

new_content = re.sub(
    r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->",
    f"<!-- PROJECTS:START -->\n{table}\n<!-- PROJECTS:END -->",
    content,
    flags=re.DOTALL,
)

if new_content != content:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"README atualizado com {len(cards)} projeto(s).")
else:
    print("Nenhuma alteração (marcadores PROJECTS:START/END não encontrados?).")
