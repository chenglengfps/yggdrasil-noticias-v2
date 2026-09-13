import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

DATA = Path("data")
FEEDS_FILE = DATA / "fontes.json"
SEEN_FILE = DATA / "publicados.json"
STATUS_FILE = DATA / "status.json"

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@YggdrasilNoticias")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")
MAX_POSTS = int(os.environ.get("MAX_POSTS_PER_RUN", "1"))

def clean_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()

def make_id(link, title):
    return hashlib.sha256((link or title).encode("utf-8")).hexdigest()

def load_feeds():
    try:
        raw = json.loads(FEEDS_FILE.read_text(encoding="utf-8"))
        return [x for x in raw if x.get("active", True) and x.get("url") and x.get("name")]
    except Exception as e:
        print(f"Erro lendo fontes.json: {e}")
        return []

def load_seen():
    if not SEEN_FILE.exists():
        return set()
    try:
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()

def save_seen(seen):
    DATA.mkdir(exist_ok=True)
    SEEN_FILE.write_text(json.dumps(list(seen)[-3000:], ensure_ascii=False, indent=2), encoding="utf-8")

def summarize(title, description):
    if not GEMINI_KEY:
        return description[:600] if description else "Confira a notícia completa no portal de origem."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    prompt = (
        "Você é editor de um canal brasileiro de notícias sobre anime, mangá e cultura pop. "
        "Faça um resumo jornalístico, claro e atraente, em no máximo 3 frases. "
        "Não invente informações.\n\n"
        f"Título: {title}\nContexto: {description}"
    )
    try:
        r = requests.post(url, params={"key": GEMINI_KEY},
                          json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=45)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini falhou: {e}")
        return description[:600] if description else "Confira a notícia completa no portal de origem."

def hashtags(title, source):
    stop={"com","para","uma","como","sobre","mais","pela","pelo","nesta","neste","este","esta","seus","suas"}
    words=re.sub(r"[^a-zA-Z0-9À-ÿ ]","",title).split()
    tags=["#"+w for w in words if len(w)>3 and w.lower() not in stop][:3]
    tags += ["#"+re.sub(r"\s+","",source), "#YggdrasilNoticias"]
    return " ".join(dict.fromkeys(tags))

def format_post(item, summary):
    return (
        "📜 Portal YGGDRASIL\n\n"
        f"📌 *{item['title']}*\n\n"
        f"{summary}\n\n"
        f"🔗 [Quer saber mais? Leia a matéria completa.]({item['link']})\n\n"
        f"✍️ Créditos ao portal: {item['source']}\n\n"
        "---\n🤝 Faça parte do nosso grupo!\n"
        f"{hashtags(item['title'], item['source'])}"
    )

def send_telegram(text):
    r=requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id":CHAT_ID,"text":text,"parse_mode":"Markdown","disable_web_page_preview":False},
        timeout=30)
    r.raise_for_status()
    if not r.json().get("ok"):
        raise RuntimeError(r.json())

def fetch_news():
    all_items=[]
    for feed in load_feeds():
        try:
            parsed=feedparser.parse(feed["url"])
            if getattr(parsed,"bozo",False):
                print(f"Aviso RSS: {feed['name']}: {getattr(parsed,'bozo_exception','erro desconhecido')}")
            for entry in parsed.entries[:15]:
                link=entry.get("link","")
                title=clean_html(entry.get("title",""))
                if not title or not link: continue
                description=clean_html(entry.get("summary",entry.get("description","")))
                published=entry.get("published",entry.get("updated",""))
                all_items.append({"id":make_id(link,title),"title":title,"link":link,
                                  "description":description,"published":published,
                                  "source":feed["name"]})
        except Exception as e:
            print(f"Falha no feed {feed['name']}: {e}")
    return all_items

def write_status(message, posts):
    STATUS_FILE.write_text(json.dumps({
        "last_run":datetime.now(timezone.utc).isoformat(),
        "message":message,"last_posts":posts
    },ensure_ascii=False,indent=2),encoding="utf-8")

def main():
    DATA.mkdir(exist_ok=True)
    feeds=load_feeds()
    if not feeds:
        write_status("Nenhuma fonte ativa configurada.", [])
        return
    seen=load_seen()
    candidates=fetch_news()
    new_items=[x for x in candidates if x["id"] not in seen][:MAX_POSTS]
    if not new_items:
        write_status("Sistema ativo — nenhuma notícia nova encontrada.", [])
        print("Nenhuma notícia nova.")
        return
    published=[]
    for item in new_items:
        try:
            send_telegram(format_post(item,summarize(item["title"],item["description"])))
            seen.add(item["id"]); published.append(item)
            print("Publicado:",item["title"])
        except Exception as e:
            print(f"Erro ao publicar {item['title']}: {e}")
    save_seen(seen)
    write_status(f"Sistema ativo — {len(published)} notícia(s) publicada(s) nesta execução.",published)

if __name__=="__main__":
    main()
