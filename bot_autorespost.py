import os
import json
import random
import urllib.request
import xml.etree.ElementTree as ET

BOT_TOKEN = os.getenv("BOT_TOKEN")
GH_PAT = os.getenv("GH_PAT")
REPO = os.getenv("GITHUB_REPOSITORY", "chenglengfps/yggdrasil-noticias-v2")
CHAT_ID = "@YggdrasilNoticias"

PORTAIS = [
    {"nome": "JBox", "url": "https://www.jbox.com.br/feed/"},
    {"nome": "O Vício", "url": "https://ovicio.com.br/category/animes/feed/"},
    {"nome": "Anime United", "url": "https://www.animeunited.com.br/feed/"},
    {"nome": "IGN Brasil", "url": "https://br.ign.com/feed.xml"},
    {"nome": "Flow Games", "url": "https://flowgames.gg/feed/"},
    {"nome": "Legião dos Heróis", "url": "https://www.legiaodosherois.com.br/feed"},
    {"nome": "TechTudo Games", "url": "https://techtudo.com.br/rss/techtudo/jogos/"}
]

HISTORICO_FILE = "postados.json"

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_historico_github(historico):
    conteudo_json = json.dumps(historico, ensure_ascii=False, indent=2)
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        f.write(conteudo_json)

    if not GH_PAT:
        print("Aviso: GH_PAT nao configurado.")
        return

    url = f"https://api.github.com/repos/{REPO}/contents/{HISTORICO_FILE}"
    headers = {
        "Authorization": f"token {GH_PAT}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }

    sha = None
    try:
        req_check = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req_check) as resp:
            data = json.loads(resp.read().decode())
            sha = data.get("sha")
    except Exception:
        pass

    content_b64 = base64.b64encode(conteudo_json.encode("utf-8")).decode("utf-8")
    payload = {"message": "Atualiza historico postados.json [skip ci]", "content": content_b64}
    if sha:
        payload["sha"] = sha

    try:
        req_put = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="PUT", headers=headers)
        with urllib.request.urlopen(req_put) as resp:
            print("✅ Historico atualizado no GitHub!")
    except Exception as e:
        print(f"⚠️ Erro ao salvar historico: {e}")

def enviar_telegram(texto):
    if not BOT_TOKEN:
        print("Erro: BOT_TOKEN ausente.")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False

def processar_feeds():
    historico = carregar_historico()
    portais_embaralhados = PORTAIS.copy()
    random.shuffle(portais_embaralhados)

    for portal in portais_embaralhados:
        try:
            nome_portal = portal["nome"]
            url_portal = portal["url"]

            req = urllib.request.Request(url_portal, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)

                channel = root.find("channel")
                items = channel.findall("item") if channel is not None else []

                for item in items[:3]:
                    link_elem = item.find("link")
                    title_elem = item.find("title")

                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    titulo = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

                    if link and (link not in historico) and (titulo not in historico):
                        tag_fonte = "#" + nome_portal.replace(" ", "")
                        msg = (
                            "🗞️ <b>PORTAL YGGDRASIL | " + nome_portal + "</b>\n\n" +
                            "🔥 <b>" + titulo + "</b>\n\n" +
                            "📖 Quer saber mais? <a href='" + link + "'>Leia a matéria completa no site!</a>\n\n" +
                            "💡 <i>Créditos ao portal " + nome_portal + "</i>\n───\n" +
                            "🌳 Faça parte do nosso canal principal: @YggdrasilAnimes\n\n" +
                            "#YggdrasilNoticias #YggdrasilAnimes #Geek #Otaku " + tag_fonte
                        )

                        if enviar_telegram(msg):
                            print(f"Postado ({nome_portal}): {titulo}")
                            historico.append(link)
                            historico.append(titulo)
                            salvar_historico_github(historico[-200:])
                            return
        except Exception as e:
            print(f"Erro portal {portal['nome']}: {e}")

if __name__ == "__main__":
    processar_feeds()
