# Instalação do perfil PedroYuri14

1. No GitHub, crie o repositório **público** `PedroYuri14/PedroYuri14` e inicialize **sem README** (para evitar conflito com os arquivos deste pacote).
2. Extraia este pacote e abra a pasta `PedroYuri14-profile` no Codex, VS Code ou terminal.
3. Execute:

```bash
git init
git branch -M main
git add .
git commit -m "feat: criar perfil Pokémon"
git remote add origin https://github.com/PedroYuri14/PedroYuri14.git
git push -u origin main
```

4. Abra a aba **Actions** do repositório. Se necessário, habilite workflows.
5. Acesse **Atualizar Pokémon Commit Map → Run workflow**. O workflow consulta a API GraphQL com `GITHUB_TOKEN` e publica o SVG.
6. Se o push automático falhar com 403, em **Settings → Actions → General → Workflow permissions**, selecione **Read and write permissions**, salve e execute novamente. Em organizações com políticas restritivas, um administrador pode precisar autorizar.
7. O mapa se atualiza diariamente (horário UTC); o agendamento pode atrasar e só roda no branch padrão.

## Ajustes
- README.md: textos, links e tecnologias.
- assets/pokemon-walk.svg: animação de caminhada (SVG e CSS).
- scripts/create_banner.py: fonte para regenerar o banner.
- assets/icons/: logos das tecnologias com fundos nas cores das marcas, baseados no [Devicon](https://github.com/devicons/devicon), sob licença MIT.
- scripts/create_tech_icons.py: regenera os 24 logos locais usando apenas a biblioteca padrão do Python.
- scripts/generate_commit_map.py: consulta GraphQL e desenho do mapa. Necessita token para rodar localmente.
- .github/workflows/update-profile.yml: automação diária.

## Limitações
- GitHub README não executa JavaScript interativo. O banner usa animações CSS dentro de SVG; alguns visualizadores, temas ou políticas de renderização podem não animar SVG. Nesse caso, converta o SVG em GIF/WebP animado e atualize o caminho no README.
- O mapa mostra o calendário de contribuições retornado pela API, não apenas commits; o GitHub define quais atividades contam e a visibilidade das contribuições privadas.
- O personagem pixel art do mapa é decorativo e não percorre a grade; o cenário se atualiza com a intensidade real das contribuições.
- Os personagens do banner são interpretações originais em pixel art, não sprites oficiais.
