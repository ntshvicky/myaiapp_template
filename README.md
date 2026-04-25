# AI Application Platform

A premium, Django-based all-in-one AI SaaS platform. This application provides a modern, glassmorphism-inspired UI with a central dashboard to access multiple AI tools, seamlessly powered by the **Google Gemini API**.

## 🌟 Key Features

*   **Modern Dashboard**: A centralized, responsive dashboard with a premium glassmorphism interface and a global sidebar for seamless navigation.
*   **Gemini AI Chatbot**: Intelligent conversational AI using a configurable Gemini model, defaulting to `gemini-2.5-flash`.
*   **Multimodal Image Chat**: Upload images and interact with them using Gemini's powerful vision capabilities.
*   **Robust Foundation**: Built on Django with integrated user authentication and an expandable service architecture.

---

## 🚀 Quick Start Guide

Follow these steps to get the project up and running locally.

### 1. Install Dependencies
Ensure you have Python installed, then install the required packages:
```bash
pip install -r requirements.txt
```
*(Note: We use `google-genai` and `python-dotenv` for AI and environment configuration)*

### 2. Environment Configuration
Create a `.env` file in the root directory (you can copy the provided `.env.example`):
```bash
cp .env.example .env
```
Open the `.env` file and add your Google Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=optional_openai_key
ANTHROPIC_API_KEY=optional_anthropic_key
SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 3. Initialize the Database
Set up your SQLite/MySQL database schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create an Admin User
Create a superuser to access the Django administration panel:
```bash
python manage.py createsuperuser
```

### 5. Run the Server
Start the development server:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser to access the new Dashboard!

---

## 🧪 Running Tests
The project includes a test suite that dynamically sets up an isolated SQLite database to ensure the views and authentication flows function correctly.
```bash
python manage.py test myaiapp
```
