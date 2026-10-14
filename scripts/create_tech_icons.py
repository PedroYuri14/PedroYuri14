"""Cria logos em cartões coloridos usando SVGs do Devicon (licença MIT)."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "icons"
REVISION = "6a37858047b0e8d9c9c0e68f4a071fc410652e89"
BASE = f"https://raw.githubusercontent.com/devicons/devicon/{REVISION}"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

# Arquivo, nome acessível, fonte Devicon, fundo, logo, preservar cores originais.
ICONS = [
    ("java", "Java", "java/java-plain", "#E76F00", "#FFFFFF", False),
    ("spring", "Spring", "spring/spring-original", "#6DB33F", "#FFFFFF", False),
    ("python", "Python", "python/python-plain", "#3776AB", "#FFFFFF", False),
    ("javascript", "JavaScript", "javascript/javascript-original", "#F7DF1E", "#181717", True),
    ("php", "PHP", "php/php-plain", "#777BB4", "#FFFFFF", False),
    ("nodejs", "Node.js", "nodejs/nodejs-plain", "#339933", "#FFFFFF", False),
    ("html", "HTML5", "html5/html5-plain", "#E34F26", "#FFFFFF", False),
    ("css", "CSS3", "css3/css3-plain", "#1572B6", "#FFFFFF", False),
    ("react", "React", "react/react-original", "#61DAFB", "#20232A", False),
    ("vite", "Vite", "vitejs/vitejs-original", "#6D28D9", "#FFFFFF", True),
    ("tailwind", "Tailwind CSS", "tailwindcss/tailwindcss-original", "#06B6D4", "#083344", False),
    ("mysql", "MySQL", "mysql/mysql-original", "#00758F", "#FFFFFF", False),
    ("postgresql", "PostgreSQL", "postgresql/postgresql-plain", "#336791", "#FFFFFF", False),
    ("mongodb", "MongoDB", "mongodb/mongodb-plain", "#47A248", "#FFFFFF", False),
    ("redis", "Redis", "redis/redis-plain", "#DC382D", "#FFFFFF", False),
    ("supabase", "Supabase", "supabase/supabase-plain", "#3ECF8E", "#13352A", False),
    ("firebase", "Firebase", "firebase/firebase-plain", "#FFCA28", "#292929", False),
    ("docker", "Docker", "docker/docker-plain", "#2496ED", "#FFFFFF", False),
    ("aws", "AWS", "amazonwebservices/amazonwebservices-plain-wordmark", "#232F3E", "#FFFFFF", False),
    ("git", "Git", "git/git-plain", "#F05032", "#FFFFFF", False),
    ("github", "GitHub", "github/github-original", "#181717", "#FFFFFF", False),
    ("vscode", "Visual Studio Code", "vscode/vscode-plain", "#007ACC", "#FFFFFF", False),
    ("idea", "IntelliJ IDEA", "intellij/intellij-original", "#C724B1", "#FFFFFF", True),
    ("postman", "Postman", "postman/postman-plain", "#FF6C37", "#FFFFFF", False),
]


def download(path):
    with urlopen(f"{BASE}/{path}", timeout=30) as response:
        return response.read()


def create_icon(icon):
    filename, name, source, background, foreground, keep_colors = icon
    logo = ET.fromstring(download(f"icons/{source}.svg"))
    if filename == "javascript":
        logo[0].set("fill", background)
    if not keep_colors:
        logo.set("fill", foreground)
        for element in logo.iter():
            for attribute in ("fill", "stroke"):
                value = element.get(attribute)
                if value and value != "none":
                    element.set(attribute, foreground)
            if "style" in element.attrib:
                element.set("style", re.sub(
                    r"(fill|stroke)\s*:\s*(?!none\b)[^;]+",
                    lambda match: f"{match.group(1)}:{foreground}",
                    element.get("style"),
                ))
    logo.attrib.update(x="12", y="12", width="40", height="40")
    tile = ET.Element(f"{{{NS}}}svg", {
        "viewBox": "0 0 64 64", "width": "64", "height": "64",
        "role": "img", "aria-label": name,
    })
    ET.SubElement(tile, f"{{{NS}}}title").text = name
    ET.SubElement(tile, f"{{{NS}}}rect", {
        "width": "64", "height": "64", "rx": "14", "fill": background,
    })
    tile.append(logo)
    ET.ElementTree(tile).write(DEST / f"{filename}.svg", encoding="utf-8")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(create_icon, ICONS))
    (DEST / "LICENSE.devicon.txt").write_bytes(download("LICENSE"))
    print(f"{len(ICONS)} logos criados em {DEST}")


if __name__ == "__main__":
    main()
