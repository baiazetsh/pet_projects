# Pet Projects Collection

This repository contains my experimental and learning projects built with Python and Django.  
Each folder represents an independent project, used to practice concepts and test ideas.

## Projects Overview

| Project            | Description                                                | Tech Stack                                   |
|--------------------|------------------------------------------------------------|----------------------------------------------|
| **blog_with_AI_bot** | Django blog extended with an AI-powered comment generator | Django, Celery, Redis, Ollama (LLM), Docker  |
| **pet_shop**         | Simple e-commerce prototype (products, cart, checkout)    | Django, SQLite/Postgres, Docker              |
| **chat_clone**       | Real-time chat clone with user profiles and messaging     | Django, Channels, WebSockets, Redis          |
| **weather_parser**   | API integration project for fetching and showing weather  | Python, Django, OpenWeatherMap API           |
| **to_do**            | Lightweight task manager for creating and tracking todos | Django, SQLite, Bootstrap                    |

## Purpose

These projects are not meant for production.  
They are part of my personal roadmap to deepen skills in:
- Python (core and advanced topics),
- Django (models, views, templates, ORM),
- Docker & Redis,
- Asynchronous tasks with Celery,
- Experimenting with local LLMs (Ollama).

## How to Run

Each project is isolated in its own folder.  
The typical workflow is:

```bash
# clone repo
git clone https://github.com/baiazetsh/pet_projects.git
cd pet_projects/project_name

# create and activate virtual environment
python -m venv venv
source venv/bin/activate    # on Linux/Mac
venv\Scripts\activate       # on Windows

# install dependencies
pip install -r requirements.txt

# apply migrations
python manage.py migrate

# run dev server
python manage.py runserver
