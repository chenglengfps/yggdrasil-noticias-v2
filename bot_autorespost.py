import os
import json
import random
import re
import urllib.request
import xml.etree.ElementTree as ET

BOT_TOKEN = os.getenv("BOT_TOKEN")
GH_PAT = os.getenv("GH_PAT")
REPO = os.getenv("GITHUB_REPOSITORY", "chenglengfps/yggdrasil-noticias-v2")
CHAT_ID = "@YggdrasilNoticias"

PORTAIS = [
    {"nome": "Voxel", "url": "https://www.tecmundo.com.br/jogos/rss"},
    {"nome": "Arkade", "url": "https://www.arkade.com.br/feed/"},
    {"nome": "GameBlast", "url": "https://www.gameblast.com.br/feeds/posts/default?alt=rss"},
    {"nome": "Meio Bit Games", "url": "https://meiobit.com/categoria/games/feed/"},
    {"nome": "Adrenaline", "url": "https://www.adrenaline.com.br/feed/"},
    {"nome": "MeuPlayStation", "url": "https://meuplaystation.com.br/feed/"},
    {"nome": "Windows Club", "url": "https://www.windowsclub.com.br/feed/"},
    {"nome": "Nintendo Blast", "url": "https://www.nintendoblast.com.br/feeds/posts/default?alt=rss"},
    {"nome": "The Enemy", "url": "https://www.theenemy.com.br/rss/feed"},
    {"nome": "Flow Games", "url": "https://flowgames.gg/feed/"},
    {"nome": "TechTudo Games", "url": "https://techtudo.com.br/rss/techtudo/jogos/"},
    {"nome": "Crunchyroll", "url": "https://www.crunchyroll.com/news/rss"},
    {"nome": "JBox", "url": "https://www.jbox.com.br/feed/"},
    {"nome": "Anime United", "url": "https://www.animeunited.com.br/feed/"},
    {"nome": "Otaku PT", "url": "https://www.otakupt.com/feed/"},
    {"nome": "Jovem Nerd", "url": "https://jovemnerd.com.br/feed/"},
    {"nome": "O Vício", "url": "https://ovicio.com.br/feed/"},
    {"nome": "Legião dos Heróis", "url": "https://www.legiaodosherois.com.br/feed/"},
    {"nome": "Garotas Geeks", "url": "https://www.garotasgeeks.com/feed/"},
    {"nome": "Nerdizmo", "url": "https://nerdizmo.com.br/feed/"},
    {"nome": "Combo Infinito", "url": "https://comboinfinito.com.br/principal/feed/"},
    {"nome": "IGN Brasil", "url": "https://br.ign.com/feed.xml"}
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

def otimizar_url_imagem(url):
    if not url:
        return None

    # Remove padroes de miniatura do Blogger / GameBlast / Google
    url = re.sub(r'/s\d+(-c)?/', '/s1600/', url)
    url = re.sub(r'/w\d+-h\d+(-[a-z0-9]+)?/', '/s1600/', url)

    # Remove sufixos de miniatura do WordPress (ex: imagem-150x150.jpg -> imagem.jpg)
    url = re.sub(r'-\d+x\d+(\.(jpg|jpeg|png|webp))', r'', url, flags=re.IGNORECASE)

    # Remove parametros de corte Jetpack/Photon (ex: ?resize=150%2C150 ou ?fit=)
    url = re.sub(r'\?(resize|fit|strip|quality)=[^&]+', '', url)

    return url

def extrair_imagem_item(item):
    url_encontrada = None

    # 1. Busca por media:content ou enclosure (versao original)
    for elem in item.iter():
        if elem.tag.endswith("content"):
            url = elem.attrib.get("url")
            if url and ("http" in url):
                url_encontrada = url
                break
        if elem.tag.endswith("enclosure"):
            url = elem.attrib.get("url")
            type_attr = elem.attrib.get("type", "")
            if url and ("image" in type_attr or "http" in url):
                url_encontrada = url
                break

    # 2. Se nao achou, busca thumbnail
    if not url_encontrada:
        for elem in item.iter():
            if elem.tag.endswith("thumbnail"):
                url = elem.attrib.get("url")
                if url and ("http" in url):
                    url_encontrada = url
                    break

    # 3. Tenta extrair tag <img> do HTML da descricao
    if not url_encontrada:
        desc = item.find("description")
        if desc is not None and desc.text:
            match = re.search(r'<img [^>]*src=["']([^"']+)["']', desc.text)
            if match:
                url_encontrada = match.group(1)

    return otimizar_url_imagem(url_encontrada)

def enviar_telegram(texto, url_imagem=None):
    if not BOT_TOKEN:
        print("Erro: BOT_TOKEN ausente.")
        return False

    if url_imagem:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload_dict = {
            "chat_id": CHAT_ID,
            "photo": url_imagem,
            "caption": texto,
            "parse_mode": "HTML"
        }
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload_dict = {
            "chat_id": CHAT_ID,
            "text": texto,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

    payload = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Erro ao enviar pelo Telegram (Photo={bool(url_imagem)}): {e}")
        if url_imagem:
            return enviar_telegram(texto, url_imagem=None)
        return False

def processar_feeds():
    historico = carregar_historico()
    portais_embaralhados = PORTAIS.copy()
    random.shuffle(portais_embaralhados)

    for portal in portais_embaralhados:
        try:
            nome_portal = portal["nome"]
            url_portal = portal["url"]

            req = urllib.request.Request(url_portal, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=15) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)

                channel = root.find("channel")
                items = channel.findall("item") if channel is not None else root.findall(".//item")

                for item in items[:3]:
                    link_elem = item.find("link")
                    title_elem = item.find("title")

                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    titulo = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

                    if link and (link not in historico) and (titulo not in historico):
                        tag_fonte = "#" + nome_portal.replace(" ", "")
                        url_imagem = extrair_imagem_item(item)

                        msg = (
                            "🗞️ <b>PORTAL YGGDRASIL | " + nome_portal + "</b>

" +
                            "🔥 <b>" + titulo + "</b>

" +
                            "📖 Quer saber mais? <a href='" + link + "'>Leia a matéria completa no site!</a>

" +
                            "💡 <i>Créditos ao portal " + nome_portal + "</i>
───
" +
                            "🌳 Faça parte do nosso canal principal: @YggdrasilAnimes

" +
                            "#YggdrasilNoticias #YggdrasilAnimes #Geek #Otaku " + tag_fonte
                        )

                        if enviar_telegram(msg, url_imagem=url_imagem):
                            print(f"Postado ({nome_portal}): {titulo}")
                            historico.append(link)
                            historico.append(titulo)
                            salvar_historico_github(historico[-200:])
                            return
        except Exception as e:
            print(f"Erro portal {portal['nome']}: {e}")

if __name__ == "__main__":
    processar_feeds()
