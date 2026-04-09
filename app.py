# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# Imports
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from newspaper import Article
from textblob import TextBlob
import nltk

nltk.download('punkt')

# API Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Flask Setup
app = Flask(__name__)
CORS(app)

# Home Route
@app.route('/')
def home():
    return "Backend is running!"

# Extract Article
def get_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

# NLP: Keywords
def get_keywords(text):
    words = text.split()
    words = [w.lower() for w in words if len(w) > 4]
    return list(set(words))[:10]

# NLP: Sentiment
def get_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Personalization Layer
def personalize_prompt(text, domain):
    if domain == "investor":
        return f"Focus on financial impact, stock market effects:\n{text}"
    elif domain == "founder":
        return f"Focus on business strategy, startup insights:\n{text}"
    else:
        return f"Explain simply for students:\n{text}"

# ML: Summarization using Transformers


# AI: Highlights
def highlights(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Give 5 important highlights:\n{text}"
        }]
    )
    return response.choices[0].message.content

# AI: Hindi Explanation
def hindi(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Explain in simple Hindi:\n{text}"
        }]
    )
    return response.choices[0].message.content

# Extra: Importance Score
def importance_score(text):
    return round(len(text) / 1000, 2)

# MAIN ROUTE
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()

        url = data.get('url')
        domain = data.get('domain', 'student')

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract article
        text = get_article(url)

        if len(text) < 100:
            return jsonify({
                "summary": "Article too short or not supported",
                "highlights": "Try another URL",
                "hindi": "यह लेख सही से प्राप्त नहीं हुआ",
                "keywords": [],
                "sentiment": "Unknown",
                "score": 0
            })

        # Apply personalization
        personalized_text = personalize_prompt(text, domain)

        # ML + AI outputs
        summary_text = summarize(text, domain)
        highlights_text = highlights(text)
        hindi_text = hindi(text)

        # NLP outputs
        keywords = get_keywords(text)
        sentiment = get_sentiment(text)
        score = importance_score(text)

        return jsonify({
            "summary": summary_text,
            "highlights": highlights_text,
            "hindi": hindi_text,
            "keywords": keywords,
            "sentiment": sentiment,
            "score": score
        })

    except Exception as e:
        print("ERROR:", e)

        return jsonify({
            "summary": "Error fetching article",
            "highlights": "Try another URL",
            "hindi": "कुछ गलत हो गया",
            "keywords": [],
            "sentiment": "Error",
            "score": 0
        })

# Run Server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)