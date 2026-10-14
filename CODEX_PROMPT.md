# Instruções para Codex

Você está trabalhando no repositório de perfil GitHub `PedroYuri14/PedroYuri14`.

## Objetivo
Aprimorar o README sem perder o estilo moderno escuro e os personagens Charmander, Gengar e Pikachu em pixel art.

## Restrições
- Preservar os workflows e o mecanismo de contribuição real via GraphQL.
- Nunca fabricar contagens de commits/contribuições.
- Não inserir JavaScript no README: GitHub não o executa.
- Usar caminhos relativos para assets, sem depender de URLs de repositórios fictícios.
- Manter acessibilidade com texto alternativo e contraste adequado.
- Evitar tokens pessoais no código e nos commits. Usar GITHUB_TOKEN do Actions.
- Não substituir o efeito por snake/cobrinha.
- Não publicar links de projetos que não estejam confirmados.

## Próximas melhorias sugeridas
1. Criar sprites mais detalhados e animação de passos de cada personagem.
2. Fazer um mapa temático com terreno, grama, árvores e Pokébolas, sem ocultar a correspondência entre dias e contribuições.
3. Criar testes unitários para renderização do SVG com dados simulados apenas em testes.
4. Melhorar a versão para dispositivos móveis e compatibilidade com tema claro.
5. Revisar os nomes das tecnologias de acordo com a experiência real do usuário.

## Validação
- Rodar `python scripts/create_banner.py`.
- Verificar se os SVGs são XML válido.
- Revisar permissões de workflow, segredos e ausência de dados inventados.
