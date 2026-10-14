# Animações do perfil

O perfil público utiliza o README da `main`. O redesign foi desenvolvido e
validado em `feature/github-profile-redesign`, com integração autorizada por Pedro.

## Animated Java IDE

Fonte: `animations/java-ide/index.html`, composição HyperFrames/GSAP de 15 segundos.
O GIF é capturado com Chromium e codificado com FFmpeg: o README não executa JavaScript.

| Tempo | Sequência |
|---|---|
| 0–2 s | A janela aparece, o explorador abre e seleciona `Developer.java`. |
| 2–9 s | Digitação progressiva, recuos, cores de sintaxe e cursor piscando. |
| 9–12 s | Terminal expande, o código rola discretamente, compila e executa. |
| 12–15 s | Confirmação verde, afastamento de 1,5% e dissolução ao início. |

O código exibido é comparado automaticamente com
`animations/java-ide/src/dev/pedroyuri/Developer.java`. O workflow compila esse arquivo
com Java 21, executa a classe e verifica a saída `Turning ideas into code.`.

Assets:

- `animated-java-ide.gif`: 1600 × 900, 10 fps, loop de 15 s.
- `animated-java-ide-mobile.gif`: recorte do editor em 1188 × 806, mesmo loop.
- `animated-java-ide-preview.png`: todo o código, antes da abertura do terminal.
- `animated-java-ide-running.png`: editor e terminal após a execução.

O README usa `<picture>` para servir o recorte no celular e a imagem estática
quando o navegador pede redução de movimento. Há também um link explícito para o PNG.
O recorte aumenta o tamanho aparente do código; a imagem em tamanho original
continua sendo a melhor opção para ler o arquivo inteiro em telas pequenas.

### Reproduzir a IDE

Requisitos: Node.js 22+, Chrome/Chromium, Python 3.12+, FFmpeg e Java 21.

```bash
python -m pip install -r scripts/requirements-render.txt
cd animations/java-ide
npm ci
npm run check
```

Defina `CHROME_PATH` com o caminho do navegador e `FFMPEG_PATH` com o executável.
Se usar o pacote Python, `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`
informa o caminho do FFmpeg. Então execute `node export.mjs`.

O exportador grava frames temporários em `.hyperframes/`, exporta os GIFs com
paleta de 128 cores e valida o Java e a ausência de transbordamento horizontal.
Não publica vídeos nem usa serviços de geração de imagens.

Para conferir o Java manualmente, dentro de `animations/java-ide`:

```bash
javac -d out src/dev/pedroyuri/Developer.java
java -cp out dev.pedroyuri.Developer
```

## Commit City

`scripts/generate_commit_city.py` usa **Python + svgwrite** para o SVG e Pillow
para as versões PNG/GIF, com a mesma geometria isométrica de aproximadamente 30°.

O calendário vem da API GraphQL `contributionCalendar` de `PedroYuri14`:
365 dias consecutivos, em ordem cronológica por fileira, sem dias futuros ou
preenchimentos externos ao período. O total é conferido contra a soma diária.
Contribuições são atividades contabilizadas pelo GitHub, não somente commits.

O snapshot `assets/commit-city-data.json` registra a fonte, usuário, período e
contagens reais. Nenhum token é gravado. Pouca atividade resulta em poucos
edifícios; terrenos vazios permanecem vazios. O teste de uma cidade densa utiliza
fixtures exclusivamente em diretórios temporários locais.

As faixas, alturas, número de colunas e animação são configuráveis em
`scripts/commit-city-config.json`. Os padrões são 0/vazio, 1–2/pequeno,
3–5/médio, 6–9/alto e 10+/arranha-céu. A legenda acompanha as faixas.

O GIF tem 1200 × 810 e 12 segundos: terrenos vazios, crescimento cronológico,
janelas iluminadas, movimento horizontal de até 8 px, pausa e retorno gradual.
O SVG estático de 1600 × 1080 contém datas e contagens nos tooltips e serve como
fallback independente de suporte a animações SVG. O PNG facilita a revisão visual.

### Reproduzir a cidade

```bash
python -m pip install -r scripts/requirements.txt
python -m unittest discover -s tests -v
python scripts/generate_commit_city.py
python scripts/validate_assets.py
```

Na geração local, defina `GITHUB_TOKEN` apenas no ambiente. Para reproduzir a
renderização sem nova consulta, use o snapshot real já salvo:

```bash
python scripts/generate_commit_city.py --input assets/commit-city-data.json
```

`--static-only` gera somente SVG, PNG e snapshot. Arquivos idênticos não são
reescritos; não há timestamp de geração, aleatoriedade ou metadados voláteis.

Se a consulta falhar, o comando retorna erro e preserva o último calendário real.
Se nenhum calendário existe, gera um SVG explicitamente marcado como
“Dados de contribuições indisponíveis”. O workflow interrompe a publicação.

## Actions e permissões

Workflow: `.github/workflows/update-commit-city.yml`, **Atualizar Commit City**.
Executa diariamente às 05:23 UTC e permite execução manual. O cron só passa
a operar após o workflow estar na branch padrão aprovada.

Para validar antes do merge, há um gatilho `push` restrito à branch
`feature/github-profile-redesign` e a arquivos de fonte/testes. Ele gera e
publica os assets nessa mesma branch. Assets gerados não acionam outro workflow.
O commit automático também inclui `[skip ci]`.

A única permissão declarada é `contents: write`, necessária para publicar os assets.
O token automático autentica a leitura do calendário público. `actions/checkout`
usa o token do Actions para o push. Não é preciso armazenar um token pessoal
se a consulta funcionar com o token padrão.

Se políticas da conta impedirem a leitura, crie o secret **PROFILE_READ_TOKEN**
em Settings → Secrets and variables → Actions. Use um token dedicado somente
para leitura do perfil; para calendário público, evite escopos de escrita.
O workflow usa esse secret na consulta e continua usando `GITHUB_TOKEN` no push.
Não coloque tokens no README, nos arquivos ou no histórico Git.

O job instala dependências fixadas, compila/executa Java, roda os testes,
consulta a API, renderiza a cidade e valida os assets. Só adiciona ao commit
os quatro arquivos `assets/commit-city.*` e `assets/commit-city-data.json`
quando existe diferença. Execuções iguais não geram commits.

Referências: [calendário e API GraphQL](https://docs.github.com/en/graphql/reference),
[secrets do Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets),
[GIF no Pillow](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif).

## Fontes e licenças

- JetBrains Mono 2.304: SIL Open Font License, incluída junto dos arquivos TTF.
- GSAP 3.14.2: distribuição oficial, com cabeçalho e README de licença preservados
  em `animations/java-ide/vendor/`; [licença oficial](https://gsap.com/standard-license/).
- Logos existentes: Devicon/MIT, licença em `assets/icons/LICENSE.devicon.txt`.

## Revisão e pendências

Previews: `assets/animated-java-ide-preview.png`, `assets/animated-java-ide-running.png`
e `assets/commit-city-preview.png`. Os GIFs podem ser vistos no README da branch.

As tecnologias foram mantidas conforme solicitado, sem reclassificar domínio.
Novos contatos aguardam os links aprovados.
