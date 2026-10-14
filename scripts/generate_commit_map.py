"""Renderiza contribuições reais do GitHub como mapa pixel art em SVG.
Usa apenas a biblioteca padrão do Python. Nunca inventa dados.
"""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets' / 'commit-map.svg'
USER = os.environ.get('PROFILE_USERNAME', 'PedroYuri14')
TOKEN = os.environ.get('GITHUB_TOKEN', '')
QUERY = '''query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}'''


def get_data():
    if not TOKEN:
        raise RuntimeError('GITHUB_TOKEN não configurado')
    payload = json.dumps({'query': QUERY, 'variables': {'login': USER}}).encode()
    req = Request('https://api.github.com/graphql', data=payload,
                  headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json',
                           'User-Agent': 'pokemon-commit-map'})
    with urlopen(req, timeout=25) as response:
        data = json.load(response)
    if data.get('errors'):
        raise RuntimeError(str(data['errors']))
    calendar = data['data']['user']['contributionsCollection']['contributionCalendar']
    return calendar['weeks'], calendar['totalContributions']


def render(weeks, total):
    width, height = 1120, 330
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Mapa de contribuições de {escape(USER)}">',
             '<style> .glow{animation:glow 3s ease-in-out infinite alternate} @keyframes glow{to{opacity:.4}} .hero{animation:bob 1.1s ease-in-out infinite alternate} @keyframes bob{to{transform:translateY(-4px)}} </style>',
             '<rect width="1120" height="330" rx="22" fill="#0c1223"/>',
             '<rect x="16" y="16" width="1088" height="298" rx="16" fill="#111d2e" stroke="#34485b"/>',
             '<text x="36" y="47" fill="#e6f3ff" font-size="21" font-family="Arial,sans-serif" font-weight="bold">POKÉMON COMMIT MAP</text>',
             f'<text x="1080" y="47" fill="#a8d3c1" font-size="14" font-family="Arial,sans-serif" text-anchor="end">{total} contribuições nos últimos 12 meses</text>',
             '<rect x="35" y="67" width="1050" height="218" rx="10" fill="#1a3441"/>']
    # Grade de 53 semanas, com 7 dias. Células 17x25 com margem de 3.
    levels = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2, 'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}
    palette = ['#264c49', '#337b58', '#44a865', '#69cf77', '#a4ee8d']
    for x, week in enumerate(weeks[-53:]):
        for y, day in enumerate(week['contributionDays']):
            lvl = levels.get(day['contributionLevel'], 0)
            px, py = 45 + x * 19.5, 79 + y * 27
            # solo pixelado, sombras e pequenos detalhes visuais por intensidade
            parts.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="16" height="21" rx="2" fill="#081e28"/>')
            parts.append(f'<rect x="{px:.1f}" y="{py-3:.1f}" width="16" height="18" rx="2" fill="{palette[lvl]}"><title>{day["date"]}: {day["contributionCount"]} contribuições</title></rect>')
            if lvl >= 2:
                parts.append(f'<rect x="{px+5:.1f}" y="{py+1:.1f}" width="3" height="5" fill="#d7ff9a" opacity=".75"/>')
            if lvl == 4:
                parts.append(f'<circle class="glow" cx="{px+12:.1f}" cy="{py+2:.1f}" r="2" fill="#fff6a8"/>')
    # Personagem original pixel-art inspirado em exploração de monstros, sem sprites copiados
    parts += ['<g class="hero" transform="translate(45 265)">',
              '<rect x="0" y="0" width="13" height="13" fill="#ffd653"/><rect x="3" y="-7" width="7" height="8" fill="#ffe987"/>',
              '<rect x="3" y="4" width="3" height="3" fill="#27203d"/><rect x="9" y="4" width="3" height="3" fill="#27203d"/>',
              '<rect x="-3" y="8" width="4" height="5" fill="#ee6b72"/><rect x="13" y="8" width="4" height="5" fill="#ee6b72"/>',
              '</g>',
              '<text x="38" y="306" fill="#a9c7d1" font-size="12" font-family="Arial,sans-serif">Menos atividade</text>']
    for i, c in enumerate(palette):
        parts.append(f'<rect x="142" y="{297}" width="0" height="0" fill="{c}"/>')  # sem legenda falsa
        parts.append(f'<rect x="{142+i*20}" y="295" width="15" height="12" rx="2" fill="{c}"/>')
    parts.append('<text x="250" y="306" fill="#a9c7d1" font-size="12" font-family="Arial,sans-serif">Mais atividade</text>')
    parts.append('</svg>')
    DEST.write_text('\n'.join(parts), encoding='utf-8')


def main():
    weeks, total = get_data()
    render(weeks, total)
    print(f'Mapa gerado com {total} contribuições reais de {USER}')


if __name__ == '__main__':
    main()
