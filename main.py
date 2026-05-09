import os
import feedparser
import requests
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

RSS_QUERIES = [
    "Chancenkarte Allemagne Maroc 2026",
    "visa travail Allemagne Marocains",
    "Decreto Flussi 2026 Maroc",
    "visa travail saisonnier Italie Maroc",
    "etudes Italie Maroc bourse",
    "visa recherche emploi Espagne Maroc 2026",
    "contrat travail temporaire Espagne Maroc",
    "Job Seeker Visa Portugal Maroc 2026",
    "immigration Canada Maroc 2026",
    "Express Entry Maroc",
    "visa etudiant Canada Maroc bourse",
    "Campus France Maroc 2026",
    "bourse etudes France Maroc",
    "bourse etudes Chine Maroc gratuite 2026",
    "Chinese Government Scholarship Maroc",
    "Turkiye Burslari bourse Maroc 2026",
    "bourse Japon Maroc MEXT 2026",
    "bourse Coree du Sud Maroc KGSP",
    "bourse Hongrie Maroc Stipendium",
    "bourse Erasmus Maroc",
    "contrat travail temporaire Europe Marocains 2026",
    "travailleur saisonnier Europe Maroc",
    "visa Schengen Maroc nouvelles regles 2026",
]

def get_news():
    print("Scan des actualites immigration Maroc...")
    query = random.choice(RSS_QUERIES)
    print(f"Recherche : {query}")
    rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=fr&gl=MA&ceid=MA:fr"
    feed = feedparser.parse(rss_url)
    if os.path.exists("history.txt"):
        with open("history.txt", "r") as f:
            history = f.read().splitlines()
    else:
        history = []
    for entry in feed.entries:
        if entry.link not in history:
            return entry, query
    return None, query

def generate_content(news_entry, query):
    print("Generation du contenu en Darija...")
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""Tu es une creatrice de contenu marocaine qui s'appelle Enami. Tu parles en Darija marocaine.
Ton audience est 100% marocaine. Ils cherchent des infos sur l'immigration et les etudes a l'etranger.
Ton style : direct, chaleureux, avec des emojis. Comme si tu parlais a une amie.
IMPORTANT : ecris TOUJOURS en Darija marocaine.

Actualite sur le sujet "{query}" :
Titre : {news_entry.title}

Genere EXACTEMENT dans ce format :

TELEGRAM:
(Resume en Darija, 3-4 phrases, infos cles : quel pays, quel visa/bourse, qui peut en beneficier. Termine par une question.)

POST_COURT:
(2 phrases percutantes en Darija pour TikTok/Reels + 5 hashtags : #ImmigrationMaroc #EtudesEtranger #EnnamiImmigration #VisaTravail #Maroc)"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        text = completion.choices[0].message.content
        parts = text.split("POST_COURT:")
        return {
            "telegram": parts[0].replace("TELEGRAM:", "").strip(),
            "post_court": parts[1].strip() if len(parts) > 1 else ""
        }
    except Exception as e:
        print(f"Erreur Groq: {e}")
        return None

def send_telegram(content, news_entry, query):
    message = f"""Enami Immigration - Actu du jour
Sujet : {query}

{content['telegram']}

---
Post pret pour TikTok/Insta/Facebook :
{content['post_court']}

Source : {news_entry.link}

Valide et poste sur tes reseaux !"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    if response.status_code == 200:
        print("Envoye sur Telegram !")
    else:
        print(f"Erreur Telegram : {response.text}")

if __name__ == "__main__":
    news, query = get_news()
    if news:
        print(f"Actu trouvee : {news.title}")
        ai_content = generate_content(news, query)
        if ai_content:
            send_telegram(ai_content, news, query)
            with open("history.txt", "a") as f:
                f.write(news.link + "\n")
    else:
        print("Pas de nouvelle actu pour le moment.")
