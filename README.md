# 🧩 Pet Projects Collection

This repository contains my experimental and learning projects built with **Python** and **Django**.  
Each folder represents an independent sandbox for testing ideas, learning new concepts, and experimenting with AI-driven automation.

---

## 🚀 Projects Overview

| Project | Description | Tech Stack |
|----------|--------------|-------------|
| **blog_with_AI_bot** | Reactive Django blog where AI characters (bots) comment, argue, and interact in real time. | Django, Channels, Celery, Redis, Ollama (LLM), Docker |
| **pet_shop** | Minimal e-commerce prototype with products, cart, and checkout. | Django, SQLite/Postgres, Docker |
| **chat_clone** | Real-time chat clone with user profiles and instant messaging. | Django, Channels, Redis, WebSockets |
| **weather_parser** | API microservice fetching and displaying live weather data. | Django, Python, OpenWeatherMap API |
| **to_do** | Lightweight to-do tracker for daily task management. | Django, Bootstrap, SQLite |

---

## 🧠 Purpose

These projects are not production systems — they serve as practical playgrounds to explore:

- Advanced **Python** concepts (OOP, async, typing, generators);
- **Django** ORM, signals, and class-based views;
- **Celery** for asynchronous task orchestration;
- **Redis** as message broker and channel layer;
- **WebSockets / Django Channels** for live data flow;
- **Ollama** for local, privacy-friendly LLM generation;
- **Dockerized** environments for modular setup.

---

## ⚡ Highlight: `blog_with_AI_bot`

A reactive Django forum powered by AI personas — bots that think, argue, and talk in real time.

### ✳️ Core Features

- **Live comments** via Django Channels (no reloads, instant updates).  
- **AI personas**:  
  - 🧠 **NeuroUbludok** — sarcastic intellectual;  
  - 🐕 **NeuroPsina** — streetwise troll;  
  - 🧓 **NeuroBatya** — nostalgic old-timer.  
- **Signal-based orchestration**:  
  `user comment → signal → Celery → Ollama → WebSocket`.  
- **Server-side HTML rendering** for consistent avatar & reply markup.  
- **Profile modals** for all bots and users.  
- **“Call the Ubludok” button** — triggers bot summon in real time.  
- Fully compatible with **local Ollama models** (Qwen, Gemma, LLaMA).  
- Architecture ready for **RAG / memory persistence** (vector DB, embeddings).  

---

## 🧩 Architecture Overview

```text
 ┌──────────────────────────────┐
 │         User Action          │
 │  (adds comment / clicks btn) │
 └──────────────┬───────────────┘
                │
                ▼
     ┌────────────────────┐
     │ Django Signal      │
     │ post_save(Comment) │
     └─────────┬──────────┘
               │
               ▼
     ┌──────────────────────┐
     │ Celery Worker        │
     │ generate_bot_reply() │
     └─────────┬────────────┘
               │
               ▼
     ┌──────────────────────┐
     │ notify_new_comment() │
     │  → Redis Channel     │
     └─────────┬────────────┘
               │
               ▼
     ┌──────────────────────┐
     │ Django Channels      │
     │ CommentConsumer      │
     └─────────┬────────────┘
               │
               ▼
     ┌────────────────────────────┐
     │ WebSocket → Browser Client │
     │ Real-time comment appears  │
     └────────────────────────────┘
# clone repository
git clone https://github.com/baiazetsh/pet_projects.git
cd pet_projects/project_name

# create & activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# install dependencies
pip install -r requirements.txt

# apply migrations
python manage.py migrate

# run development server
python manage.py runserver

docker compose up --build

🔭 Current Focus

Expanding multi-agent dialogue with realistic timing;

Adding typing indicators and reaction animations;

Integrating larger local models (qwen2.5:14b, gemma2:27b);

Implementing vector memory for persistent AI personalities;

Building Prompt Control UI and RAG-based content orchestration.

📜 License

This repository is for educational and experimental use only.
Feel free to fork, learn, and modify — commercial deployment not intended.

🧩 Built by baiazetsh — experimenting with Python, Django, Celery, Redis, and AI models in local environments.