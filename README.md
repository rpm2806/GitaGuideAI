# 🕉️ GitaGuide AI - Your Spiritual Companion

![GitaGuide AI Banner](https://img.shields.io/badge/GitaGuide-AI-orange?style=for-the-badge&logo=meditation)
![Next.js](https://img.shields.io/badge/Next.js-15.1-black?style=flat-square&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4.0-38B2AC?style=flat-square&logo=tailwind-css)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black?style=flat-square&logo=vercel)
![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render)

**GitaGuide AI** is an advanced, spiritually-aware chatbot designed to provide wisdom and guidance based on the eternal teachings of the **Bhagavad Gita**. It combines modern AI with ancient scripture to offer personalized, context-aware answers to life's most profound questions.

---

## 🚀 Live Demo

- **Frontend (Chat Interface):** [https://gita-guide-ai.vercel.app](https://gita-guide-ai.vercel.app)
- **Backend (API):** [https://gitaguideai-backend.onrender.com](https://gitaguideai-backend.onrender.com) (Swagger UI at `/docs`)

---

## ✨ Key Features

- **Context-Aware Wisdom:** Uses RAG (Retrieval-Augmented Generation) to fetch relevant verses from the Bhagavad Gita based on your query.
- **Multilingual Support:** Ask questions and receive answers in **English** or **Hindi**.
- **Mood-Based Responses:** Tailors the tone of the guidance based on your current emotional state (e.g., Sad, Anxious, Angry, Seeking Purpose).
- **Sacred Verses Integration:** Every response includes the specific Sanskrit shlokas, transliterations, and translations that inspired the advice.
- **"Spiritually Modern" UI:** A beautiful, responsive interface featuring glassmorphism, smooth animations, and a day/night mode (Sun/Moon themes).
- **Audio/Voice Friendly:** (Coming Soon) planned integration for voice input and text-to-speech.

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework:** [Next.js 15](https://nextjs.org/) (App Router, Server Components)
- **Styling:** [Tailwind CSS 4](https://tailwindcss.com/) + Custom CSS Variables
- **Icons:** [Lucide React](https://lucide.dev/)
- **State Management:** React Hooks (`useState`, `useEffect`, `useRef`)
- **Deployment:** Vercel

### **Backend**
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11)
- **AI Model:** [Groq API](https://groq.com/) (Llama-3-8b-8192 for ultra-fast inference)
- **Vector Search:** `httpx` + Hugging Face Inference API (`BAAI/bge-small-en-v1.5`)
- **Database:** In-memory vector store (optimized for 700+ verses)
- **Deployment:** Render (Free Tier Optimized)

---

## ⚙️ Local Setup

Follow these steps to run GitaGuide AI locally on your machine.

### **1. Clone the Repository**
```bash
git clone https://github.com/rpm2806/GitaGuideAI.git
cd GitaGuideAI
```

### **2. Backend Setup**
Navigate to the backend folder and set up the Python environment.
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_with_inference_permission
CORS_ORIGINS=http://localhost:3000
```

Run the server:
```bash
uvicorn main:app --reload
# Backend will run at http://localhost:8000
```

### **3. Frontend Setup**
Open a new terminal and navigate to the frontend folder.
```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the development server:
```bash
npm run dev
# Frontend will run at http://localhost:3000
```

---

## 📚 API Documentation

The backend exposes the following endpoints:

### `GET /`
Returns a welcome message to verify the API is running.

### `POST /chat`
The main endpoint for the chat interface.
- **Body:**
  ```json
  {
    "message": "I feel lost and confused about my duty.",
    "language": "en",
    "mood": "Confused"
  }
  ```
- **Response:**
  ```json
  {
    "response": "Arjuna, do not yield to this degrading impotence...",
    "relevant_verses": [
      {
        "chapter": 2,
        "verse": 3,
        "text": "...",
        "shloka": "...",
        "transliteration": "..."
      }
    ]
  }
  ```

### `GET /health`
Health check endpoint for monitoring uptime.

---

## ☁️ Deployment Guide

### **Backend (Render)**
1.  Connect your GitHub repo to Render.
2.  Select "Web Service" and point to the `backend` directory.
3.  **Build Command:** `pip install -r requirements.txt`
4.  **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables:** Add `GROQ_API_KEY`, `HF_TOKEN`, and `PYTHON_VERSION` (3.11.9).

### **Frontend (Vercel)**
1.  Connect your GitHub repo to Vercel.
2.  Select the `frontend` directory as the **Root Directory**.
3.  **Environment Variables:** Add `NEXT_PUBLIC_API_URL` set to your Render backend URL.
4.  Click **Deploy**.

---

## � Credits & Acknowledgements

- **Prophet of AI:** For the inspiration to build agentic AI applications.
- **Bhagavad Gita:** The timeless source of wisdom.
- **Open Source Community:** For the amazing tools and libraries.

*May wisdom guide you.* 🕉️
