# Django Restaurant Ordering App (Ready to run)

## Overview
- Django project `restaurant_project` with app `orders`.
- User registration & login (Django auth).
- Menu endpoint (`/api/menu`) proxies to external restaurant API or serves `sample_menu.json`.
- Cart stored in session; add/remove/update quantity via AJAX endpoints.
- Place order endpoint saves orders to MySQL `restaurant_app` DB (defaults: root@localhost, no password).
- Chatbot endpoint (`/api/chat/`) that forwards messages to OpenRouter (meta-llama/llama-3.3-70b-instruct) using your OpenRouter API key.

## Quick setup
1. Create virtualenv and install:
   ```bash
   python -m venv venv
   source venv/bin/activate   # mac/linux
   venv\Scripts\activate    # windows
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set values (especially `OPENROUTER_API_KEY`).
3. Start MySQL and ensure user `root`@`localhost` with empty password exists or update `.env`.
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```
6. Run the server:
   ```bash
   python manage.py runserver
   ```
7. Open `http://127.0.0.1:8000/`.

## Notes
- The app will create necessary tables via migrations. Orders are saved in `orders.Order` model.
- For development/testing you can leave `RESTAURANT_API_URL` empty to use `sample_menu.json`.
- The OpenRouter API key should be put in `.env` as `OPENROUTER_API_KEY`.

## Files included
- `restaurant_project/` - Django project
- `orders/` - Django app with models, views, templates, static
- `.env.example`, `sample_menu.json`, `requirements.txt`
