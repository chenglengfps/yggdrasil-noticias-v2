<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Yggdrasil Notícias</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #4CAF50; }
        .info-box { background: #1e1e1e; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #4CAF50; }
        .portal-card { background: #1e1e1e; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; }
        .portal-name { font-size: 1.1em; font-weight: bold; color: #64B5F6; margin-bottom: 5px; }
        .previa-box { background: #2a2a2a; padding: 10px; border-radius: 5px; font-size: 0.9em; margin: 10px 0; color: #ccc; }
        .btn-enviar { background-color: #FF9800; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; }
        .btn-enviar:hover { background-color: #e68a00; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Yggdrasil Notícias v2</h1>
        
        <div class="info-box">
            <p><strong>Status do Bot:</strong> Ativo</p>
            <p><strong>Intervalo de envio:</strong> 30 minutos entre portais</p>
        </div>

        <h2>Portais Cadastrados</h2>
        <div id="lista-portais">Carregando portais...</div>
    </div>

    <script>
        async function carregarPortais() {
            try {
                const res = await fetch('data/fontes.json');
                const portais = await res.json();
                const container = document.getElementById('lista-portais');
                container.innerHTML = '';

                portais.forEach((portal, index) => {
                    const card = document.createElement('div');
                    card.className = 'portal-card';
                    card.innerHTML = `
                        <div class="portal-name">${portal.nome}</div>
                        <div class="previa-box" id="previa-${index}">Buscando última notícia...</div>
                        <button class="btn-enviar" onclick="enviarTeste('${portal.url}', ${index})">🚀 Enviar Agora (Teste)</button>
                    `;
                    container.appendChild(card);
                    carregarPrevia(portal.url, index);
                });
            } catch (e) {
                document.getElementById('lista-portais').innerText = 'Erro ao carregar fontes.json';
            }
        }

        async function carregarPrevia(feedUrl, index) {
            try {
                const res = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(feedUrl)}`);
                const data = await res.json();
                if (data.items && data.items.length > 0) {
                    document.getElementById(`previa-${index}`).innerText = "Última: " + data.items[0].title;
                } else {
                    document.getElementById(`previa-${index}`).innerText = "Nenhuma notícia recente no feed.";
                }
            } catch (e) {
                document.getElementById(`previa-${index}`).innerText = "Não foi possível carregar a prévia.";
            }
        }

        function enviarTeste(feedUrl, index) {
            alert(`Solicitação de envio enviada para o portal #${index + 1}! O bot processará a notícia no próximo ciclo.`);
        }

        carregarPortais();
    </script>
</body>
</html>

