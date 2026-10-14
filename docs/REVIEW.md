# Redesign para revisão

Branch: `feature/github-profile-redesign`. A `main` continua no commit
`7436037e63f0f491b02b03b2feb76c8088b36208`, sem publicação do redesign.

## Previews

- [Perfil completo, desktop](./previews/profile-desktop.png)
- [Perfil completo, celular](./previews/profile-mobile.png)
- [Prévia navegável local](./review.html)
- [IDE animada](../assets/animated-java-ide.gif)
- [IDE com todo o código](../assets/animated-java-ide-preview.png)
- [IDE após execução](../assets/animated-java-ide-running.png)
- [Cidade animada](../assets/commit-city.gif)
- [Cidade estática](../assets/commit-city.svg)

Abra `docs/review.html` em um navegador para a prévia local animada. No GitHub,
abra o README da branch para conferir o resultado servido pelo próprio GitHub.

## Arquivos modificados

| Grupo | Alterações |
|---|---|
| Perfil | `README.md` reorganizado e `SETUP.md` atualizado; tecnologias preservadas. |
| IDE | `animations/java-ide/`: composição, fonte Java, fonte tipográfica, GSAP, exportador e dependências fixadas. |
| Banner | GIF 1600 × 900 de 15 s, recorte para celular e dois PNGs estáticos. |
| Cidade | `scripts/generate_commit_city.py`, configuração e dependências; SVG, PNG, GIF e snapshot real. |
| Automação | `.github/workflows/update-commit-city.yml`, atualização diária/manual e validação na feature branch. |
| Qualidade | `tests/test_commit_city.py`, `scripts/validate_assets.py`, preview e documentação. |
| Remoções | Banner, mapa, geradores, workflow e prompt antigos do tema anterior. |

## Evidências de validação

- Java 21 compilado e executado localmente; saída exata `Turning ideas into code.`.
- Mesma compilação e execução concluídas no Actions.
- 8 testes locais e no Actions: faixas, dias vazios, ordem, contagens inválidas,
  calendário incompleto, total, ausência de token, placeholder e determinismo.
- HyperFrames: lint, runtime, layout e movimento sem erros; 9 amostras de layout
  e 941 verificações de contraste aprovadas.
- Todos os frames dos GIFs decodificados; dimensões, loop infinito, durações
  de 15/12 s e continuidade do banner conferidas.
- GIF desktop com aproximadamente 1,63 MiB, celular 1,06 MiB e cidade 0,78 MiB.
- Calendário real de 365 dias, com 4 contribuições em 3 dias ativos na consulta.
  Os três edifícios correspondem exatamente a esses dias; nenhum dia vazio recebe edifício.
- GitHub Markdown API preservou `<picture>`, media query para celular e fallback
  de redução de movimento. Navegador carregou 27 imagens em desktop e celular.
- GIF publicado na feature branch respondeu HTTP 200 e `Content-Type: image/gif`.
- [Execução inicial do Actions aprovada](https://github.com/PedroYuri14/PedroYuri14/actions/runs/38574205192),
  incluindo leitura via `GITHUB_TOKEN` e publicação na branch de trabalho.
- O workflow também compara os hashes dos quatro assets após duas renderizações
  do mesmo snapshot, impedindo a publicação de resultados não determinísticos.

O primeiro render no Linux substituiu apenas PNG/GIF renderizados no Windows:
a versão do rasterizador da fonte pode variar entre sistemas. A geração diária
usa o mesmo ambiente Ubuntu com Pillow fixado. SVG e dados permaneceram idênticos.

## Pendências

1. Aprovação visual e autorização explícita para integrar na `main`.
2. Envio dos novos links de contato, conforme combinado.

O cron diário só passa a executar o novo workflow quando ele estiver na branch
padrão. Até a aprovação, o perfil público continua com a versão anterior.

Detalhes de geração e permissões: [ANIMATIONS.md](./ANIMATIONS.md).
