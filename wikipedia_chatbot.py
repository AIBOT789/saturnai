import streamlit as st
import streamlit.components.v1 as components
import os
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import re
import requests
import time
from textblob import TextBlob

# Google Analytics integration for Search Console verification
components.html(
    """
    <!-- Google Analytics -->
    <script async src='https://www.googletagmanager.com/gtag/js?id=G-QJ9RY025XV'></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-QJ9RY025XV');
    </script>
    """,
    height=0,
    width=0
)

YOUTUBE_API_KEY = "AIzaSyALoTMUXxQaWVIB6PW4-YJeNuxOtlaNT6Y"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# Custom CSS for liquid color background and chat UI
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%) !important;
    }
    .stApp {
        background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%) !important;
    }
    .chat-bubble {
        background: rgba(255,255,255,0.85);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-size: 1.1em;
        color: #222;
    }
    .user-bubble {
        background: #185a9d;
        color: #fff;
        text-align: right;
        border-radius: 20px 20px 4px 20px;
    }
    .bot-bubble {
        background: #43cea2;
        color: #222;
        border-radius: 20px 20px 20px 4px;
    }
    .send-btn {
        background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-size: 1em;
        cursor: pointer;
        margin-left: 8px;
    }
    .video-frame {
        margin: 10px 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    .fixed-bottom-input {
        position: fixed;
        left: 50%;
        bottom: 32px;
        transform: translateX(-50%);
        width: 40vw;
        min-width: 350px;
        max-width: 600px;
        background: none;
        z-index: 9999;
        padding: 0;
        margin: 0 auto;
        box-shadow: none;
        display: flex;
        justify-content: center;
    }
    .fixed-bottom-inner {
        width: 100%;
        display: flex;
        background: #23232b;
        border-radius: 10px;
        box-shadow: 0 2px 12px rgba(24,90,157,0.10);
        align-items: center;
        padding: 0 0.5em;
    }
    .fixed-bottom-inner input {
        background: none;
        border: none;
        color: #fff;
        width: 100%;
        font-size: 1.2em;
        padding: 1em 0.5em;
        outline: none;
    }
    .fixed-bottom-inner button {
        background: #111;
        color: #fff;
        border: none;
        border-radius: 6px;
        padding: 0.7em 1.5em;
        font-size: 1.1em;
        margin-left: 0.5em;
        cursor: pointer;
        transition: background 0.2s;
    }
    .fixed-bottom-inner button:hover {
        background: #185a9d;
    }
    .stApp {
        padding-bottom: 120px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='color:#fff;text-align:center;'>Neptune AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#fff;text-align:center;'>Ask me anything! I'll fetch the answer from Wikipedia or suggest YouTube videos.</p>", unsafe_allow_html=True)

# Session state for chat history
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Predefined responses for common greetings and questions
def get_predefined_response(query):
    q = query.lower().strip()
    if q in ["hello", "hi", "hey"]:
        return "Hello! How can I help you today?"
    if q in ["how are you", "how are you?", "how are you doing?"]:
        return "I'm an AI Wikipedia chatbot, so I'm always ready to help!"
    if q in ["who are you", "who are you?", "what are you?"]:
        return "I'm a chatbot that fetches information from Wikipedia."
    if q in ["what do you do", "what do you do?", "what can you do?"]:
        return "I answer your questions using information from Wikipedia."
    return None

# Detect language from the query (simple keyword-based)
def detect_language(query):
    match = re.search(r"in ([a-zA-Z]+)", query.lower())
    if match:
        lang = match.group(1)
        lang_map = {
            "hindi": "hi",
            "english": "en",
            "french": "fr",
            "spanish": "es",
            "german": "de",
            "japanese": "ja",
            "chinese": "zh",
            "russian": "ru",
            "arabic": "ar",
            "italian": "it",
            "portuguese": "pt",
        }
        return lang_map.get(lang, "en")
    return "en"

# YouTube Data API integration to fetch top videos
def get_youtube_videos(query, max_results=10):
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        videos = []
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]
            videos.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": thumbnail
            })
        return videos
    return []

def correct_spelling(text):
    blob = TextBlob(text)
    return str(blob.correct())

# Display chat history (oldest to newest)
for i, msg in enumerate(st.session_state['history']):
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble user-bubble">{msg["text"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "bot":
        if "image" in msg:
            st.image(msg["image"], caption="Image from Wikipedia", use_column_width=True)
        if "videos" in msg:
            st.markdown(f'<div class="chat-bubble bot-bubble">{msg["text"]}</div>', unsafe_allow_html=True)
            for v in msg["videos"]:
                st.markdown(f'''<div class="video-frame" style="background: #fff; border: 2px solid #43cea2; border-radius: 16px; margin: 16px 0; box-shadow: 0 4px 16px rgba(24,90,157,0.15);">
                    <a href="{v["url"]}" target="_blank" style="text-decoration:none;">
                        <img src="{v["thumbnail"]}" width="100%" style="border-radius: 12px 12px 0 0;">
                        <div style="padding: 12px; font-size: 1.1em; color: #185a9d; font-weight: bold;">{v["title"]}</div>
                    </a>
                </div>''', unsafe_allow_html=True)
        elif "text" in msg:
            # Typing animation for the latest bot message only
            if i == len(st.session_state['history']) - 1 and st.session_state['history'][-1]['role'] == 'bot' and 'typing_done' not in st.session_state:
                placeholder = st.empty()
                bot_text = msg["text"]
                displayed = ""
                for char in bot_text:
                    displayed += char
                    placeholder.markdown(f'<div class="chat-bubble bot-bubble">{displayed}</div>', unsafe_allow_html=True)
                    time.sleep(0.01)
                st.session_state['typing_done'] = True
            else:
                st.markdown(f'<div class="chat-bubble bot-bubble">{msg["text"]}</div>', unsafe_allow_html=True)

# Fixed chat input at the bottom center
st.markdown('<div class="fixed-bottom-input"><div class="fixed-bottom-inner">', unsafe_allow_html=True)
col1, col2 = st.columns([5,1], gap="small")
with col1:
    user_input = st.text_input("Your question:", key="user_input", placeholder="Type your message...", label_visibility="collapsed")
with col2:
    send = st.button("Send", key="send_btn")
st.markdown('</div></div>', unsafe_allow_html=True)

if send and user_input:
    if 'typing_done' in st.session_state:
        del st.session_state['typing_done']
    st.session_state['history'].append({"role": "user", "text": user_input})
    predefined = get_predefined_response(user_input)
    video_match = re.search(r'suggest me some (.+?) video', user_input.lower())
    # If 'video' is in the prompt, search YouTube for the topic
    if predefined:
        st.session_state['history'].append({"role": "bot", "text": predefined})
    elif 'video' in user_input.lower():
        # Use the whole prompt minus 'video' for search
        topic = user_input.lower().replace('video', '').strip()
        topic = correct_spelling(topic)
        videos = get_youtube_videos(topic, 10)
        st.session_state['history'].append({"role": "bot", "videos": videos, "text": f"Here are the top 10 {topic.title()} videos for you:"})
    else:
        # Correct spelling for Wikipedia queries
        clean_query = correct_spelling(user_input)
        lang_code = detect_language(clean_query)
        wikipedia.set_lang(lang_code)
        clean_query = re.sub(r"in [a-zA-Z]+", "", clean_query, flags=re.IGNORECASE).strip()
        try:
            page = wikipedia.page(clean_query)
            summary = page.content
            # Add gap between each paragraph
            summary = '\n\n'.join([p.strip() for p in summary.split('\n') if p.strip()])
            if page.images:
                image_url = next((img for img in page.images if not any(x in img.lower() for x in ["logo", "icon", "svg", "flag"])), page.images[0])
                st.session_state['history'].append({"role": "bot", "text": summary, "image": image_url})
            else:
                st.session_state['history'].append({"role": "bot", "text": summary})
        except DisambiguationError as e:
            st.session_state['history'].append({"role": "bot", "text": f"Your query is ambiguous. Suggestions: {e.options[:5]}"})
        except PageError:
            st.session_state['history'].append({"role": "bot", "text": "Sorry, I couldn't find anything on Wikipedia for that query."})
        except Exception as ex:
            st.session_state['history'].append({"role": "bot", "text": f"An error occurred: {ex}"})
    st.rerun()
