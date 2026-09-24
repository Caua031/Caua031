import os
import re
import json
import urllib.request

USERNAME = os.environ.get("GH_USERNAME", "Caua031")
TOKEN = os.environ.get("GH_TOKEN")
MAX_REPOS = 6

url = f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=100"
headers = {"Accept": "application/vnd.github+json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    repos = json.load(resp)

repos = [r for r in repos if not r.get("fork") and r["name"].lower() != USERNAME.lower()]
repos = repos[:MAX_REPOS]

LANG_ICON = {
    "Python": "python", "JavaScript": "javascript", "HTML": "html",
    "CSS": "css", "C": "c", "TypeScript": "typescript", "Java": "java",
    "Jupyter Notebook": "python", "Shell": "bash",
}

def card(r):
    icon = LANG_ICON.get(r.get("language") or "", "")
    icon_html = f'<img src="https://skillicons.dev/icons?i={icon}" height="24"/>\n\n' if icon else ""
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
