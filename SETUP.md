# Perfil PedroYuri14

O redesign está na branch `feature/github-profile-redesign`, aguardando aprovação
para integração na `main`. Abra o README dessa branch para revisar as animações.

As instruções de geração, testes, permissões, fontes e fallbacks estão em
[docs/ANIMATIONS.md](./docs/ANIMATIONS.md).

Após o merge aprovado, abra **Actions → Atualizar Commit City → Run workflow**.
A atualização diária está agendada para 05:23 UTC. O workflow usa `GITHUB_TOKEN`
e a permissão `contents: write`; não adicione credenciais ao código.

Os 24 logos continuam em `assets/icons/`. Para regenerá-los, execute
`python scripts/create_tech_icons.py`.
