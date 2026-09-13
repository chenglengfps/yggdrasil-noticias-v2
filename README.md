# Yggdrasil Notícias — V2

Painel estático + robô Python para GitHub Actions.

## O que mudou

- Painel com status do robô.
- Campos locais para Telegram/Gemini: ficam salvos no navegador e não entram no GitHub.
- Cadastro, teste, ativação, pausa, edição e exclusão de fontes RSS.
- Catálogo persistente do robô em `data/fontes.json`.
- Exportação/importação do catálogo pelo painel.
- Robô consulta fontes ativas a cada 2 horas.
- Até 1 notícia por execução por padrão.
- Telegram e Gemini usam GitHub Actions Secrets.

## Importante sobre segurança

Nunca coloque token do Telegram ou chave Gemini em `index.html`, `bot.py`, `fontes.json` ou qualquer arquivo público.

Os campos de API do painel são apenas conveniência local. O robô 24/7 lê os valores dos GitHub Actions Secrets.

## Como publicar uma nova fonte

1. No painel, informe nome e RSS.
2. Clique em `Testar fonte`.
3. Confira as notícias de exemplo.
4. Clique em `Adicionar ao catálogo`.
5. Clique em `Baixar catálogo`.
6. No GitHub, substitua `data/fontes.json` pelo arquivo baixado e faça o commit.
7. Na próxima execução, o robô já poderá consultar a nova fonte.

## GitHub Secrets

Crie:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `GEMINI_API_KEY`

`GEMINI_API_KEY` é opcional. Sem ela, o robô usa a descrição do RSS como resumo.

## GitHub Pages

Em Settings > Pages, escolha a branch `main` e a pasta `/ (root)`.
O site será publicado pelo GitHub Pages.
