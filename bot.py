import os
import json
import time
import feedparser
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env local
load_dotenv()

# CONFIGURAÇÕES DE API (Lidas estritamente do arquivo .env local)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ARQUIVOS DE DADOS LOCAIS
PATH_FONTES = "data/fontes.json"
PATH_PUBLICADOS = "data/publicados.json"
PATH_STATUS = "data/status.json"

# CONFIGURAÇÕES DE TEMPO (em segundos)
INTERVALO_ENTRE_PORTAIS = 1800  # 30 minutos entre envios de portais diferentes
INTERVALO_CHECAGEM_GERAL = 900  # 15 minutos de pausa ao concluir um ciclo completo

def carregar_json(caminho, padrao):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"✖ Erro ao ler {caminho}: {e}")
    return padrao

def salvar_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠ Token do Telegram ou CHAT_ID não configurados no arquivo .env!")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"✖ Erro ao conectar com API do Telegram: {e}")
        return False

def processar_ciclo():
    fontes = carregar_json(PATH_FONTES, [])
    publicados = carregar_json(PATH_PUBLICADOS, [])
    
    if not fontes:
        print("⚠ Nenhuma fonte encontrada em data/fontes.json.")
        return

    print("\n🔄 Iniciando verificação dos portais...")

    for portal in fontes:
        nome_portal = portal.get("nome", "Portal Sem Nome")
        url_feed = portal.get("url")

        if not url_feed:
            continue

        print(f"\n📡 Lendo: {nome_portal}")
        try:
            feed = feedparser.parse(url_feed)
        except Exception as e:
            print(f"✖ Falha ao ler feed de {nome_portal}: {e}")
            continue

        noticia_enviada_neste_portal = False

        for entry in feed.entries:
            link = entry.get("link")
            titulo = entry.get("title")

            if not link or link in publicados:
                continue

            # Monta a mensagem formatada
            mensagem = f"<b>{titulo}</b>\n\nFonte: {nome_portal}\n🔗 {link}"
            
            print(f"🚀 Enviando notícia: {titulo}")
            if enviar_telegram(mensagem):
                publicados.append(link)
                salvar_json(PATH_PUBLICADOS, publicados)
                noticia_enviada_neste_portal = True
                break  # Envia apenas 1 notícia por portal por ciclo para manter o rodízio
            else:
                print(f"✖ Falha no envio da notícia: {titulo}")

        # Se enviou uma notícia, aguarda 30 minutos antes de passar para o próximo portal
        if noticia_enviada_neste_portal:
            print(f"⏳ Aguardando {INTERVALO_ENTRE_PORTAIS // 60} minutos antes do próximo portal...")
            time.sleep(INTERVALO_ENTRE_PORTAIS)

    # Atualiza o timestamp do último ciclo no arquivo de status
    salvar_json(PATH_STATUS, {"ultimo_ciclo": time.strftime("%Y-%m-%d %H:%M:%S")})

if __name__ == "__main__":
    print("🤖 Bot Yggdrasil Notícias iniciado com sucesso!")
    while True:
        processar_ciclo()
        print(f"\n💤 Ciclo finalizado. Checagem geral em {INTERVALO_CHECAGEM_GERAL // 60} minutos...")
        time.sleep(INTERVALO_CHECAGEM_GERAL)
	

