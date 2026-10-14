from pathlib import Path
root=Path(__file__).resolve().parents[1]
svg=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 260" role="img" aria-label="Charmander, Gengar e Pikachu caminhando em um mundo pixel art">
<style>
.walk1{animation:move1 16s linear infinite}.walk2{animation:move2 19s linear infinite}.walk3{animation:move3 14s linear infinite}.bob{animation:bob .45s steps(2) infinite alternate}.spark{animation:twinkle 2s ease-in-out infinite alternate}
@keyframes move1{from{transform:translateX(-160px)}to{transform:translateX(1130px)}}
@keyframes move2{from{transform:translateX(-440px)}to{transform:translateX(850px)}}
@keyframes move3{from{transform:translateX(-730px)}to{transform:translateX(560px)}}
@keyframes bob{to{transform:translateY(-5px)}}@keyframes twinkle{to{opacity:.15}}
</style>
<rect width="1100" height="260" rx="18" fill="#101829"/>
<circle cx="922" cy="50" r="29" fill="#e8dca3" opacity=".85"/>
<path d="M0 151 L95 109 175 151 285 99 403 154 505 107 642 149 746 101 866 150 972 108 1100 152V260H0Z" fill="#1b3741"/>
<path d="M0 179L100 162 220 176 335 151 480 176 650 155 800 173 960 151 1100 171V260H0Z" fill="#285347"/>
<rect y="199" width="1100" height="61" fill="#2e6749"/><rect y="213" width="1100" height="47" fill="#23493e"/>
<path d="M0 200H1100" stroke="#6ec486" stroke-width="5"/>
<g fill="#90d899">''']
for x in range(22,1100,53):
 svg.append(f'<path d="M{x} 201l-5 -9m5 9l5 -12" stroke="#90d899" stroke-width="2"/>')
svg.append('</g>')
for x,y in [(70,55),(240,39),(410,80),(590,45),(760,64),(1040,93)]:
 svg.append(f'<circle class="spark" cx="{x}" cy="{y}" r="2" fill="#d8f6c4"/>')
# rect pixel sprites: small bespoke vector characters
sprites={
'charmander': [(' #f58a43',[(4,1,7,2),(3,3,9,6),(4,9,8,5),(5,14,7,3),(3,17,4,2),(10,17,4,2),(1,11,4,3),(12,11,3,3),(0,14,3,3)]),('#ffd3a1',[(6,10,5,5)]),('#1b2338',[(5,5,2,2),(10,5,2,2)]),('#ffda51',[(0,11,2,3)]),('#ff634d',[(0,9,2,3)])],
'gengar': [('#8e68c9',[(3,4,12,12),(1,8,16,7),(3,15,13,4),(0,5,4,5),(14,5,4,5),(2,2,3,5),(6,0,3,5),(11,1,3,5)]),('#f8e9fb',[(4,8,4,4),(11,8,4,4)]),('#e84b67',[(5,9,3,2),(12,9,3,2)]),('#22243b',[(4,15,11,1),(7,16,2,1),(11,16,2,1)])],
'pikachu': [('#f8d958',[(4,4,10,9),(3,13,12,5),(3,18,4,2),(11,18,4,2),(1,1,3,10),(14,0,3,10),(16,11,4,3),(19,9,3,3)]),('#272339',[(1,1,3,3),(14,0,3,3),(6,8,2,2),(12,8,2,2)]),('#e66c67',[(4,11,3,2),(13,11,3,2)]),('#fff4a5',[(8,13,4,3)])]}
for i,(name,groups) in enumerate(sprites.items()):
 svg.append(f'<g class="walk{i+1}"><g class="bob" transform="translate(0 116)" shape-rendering="crispEdges">')
 for color,rects in groups:
  for x,y,w,h in rects:
   svg.append(f'<rect x="{x*4}" y="{y*4}" width="{w*4}" height="{h*4}" fill="{color.strip()}"/>')
 svg.append('</g></g>')
svg.append('<text x="25" y="32" fill="#e5f6ff" font-family="Arial,sans-serif" font-weight="bold" font-size="17">PEDROYURI14  /  DEV JOURNEY</text></svg>')
(root/'assets'/'pokemon-walk.svg').write_text('\n'.join(svg),encoding='utf8')
