import os
import json
import urllib.request
import xml.etree.ElementTree as ET

BOT_TOKEN = os.getenv("BOT_TOKEN")
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

def salvar_historico(historico):
    try:
        with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Aviso historico: {e}")

def enviar_telegram(texto):
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN não encontrado nas variáveis de ambiente.")
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
        print(f"❌ Erro Telegram: {e}")
        return False

def processar_feeds():
    historico = carregar_historico()

    for portal in PORTAIS:
        try:
            req = urllib.request.Request(portal["url"], headers={"User-Agent": "Mozilla/5.0"})
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

                    if link and link not in historico:
                        tag_fonte = "#" + portal["nome"].replace(" ", "")
                        msg = (
                            f"🗞️ <b>PORTAL YGGDRASIL | {portal['nome']}</b>

"
                            f"🔥 <b>{titulo}</b>

"
                            f"📖 Quer saber mais? <a href='{link}'>Leia a matéria completa no site!</a>

"
                            f"💡 <i>Créditos ao portal {portal['nome']}</i>
───
"
                            f"🌳 Faça parte do nosso canal principal: @YggdrasilAnimes

"
                            f"#YggdrasilNoticias #YggdrasilAnimes #Geek #Otaku {tag_fonte}"
                        )

                        if enviar_telegram(msg):
                            print(f"✅ Postado: {titulo}")
                            historico.append(link)
                            salvar_historico(historico)
                            return
        except Exception as e:
            print(f"⚠️ Erro portal {portal['nome']}: {e}")

if __name__ == "__main__":
    processar_feeds()
