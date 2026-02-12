# 🕉️ GitaGuide AI

**GitaGuide AI** is a spiritually modern, spiritually modern, and emotion-aware assistant grounded strictly in the wisdom of the **Bhagavad Gita**. It provides spiritual guidance, practical reflection, and gentle advice based on authentic scriptural verses.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Groq](https://img.shields.io/badge/LLM-Llama%203.1%20(Groq)-orange)

---

## ✨ Features

*   **📖 Scriptural Grounding**: Every response is rooted in retrieved verses from the Gita, avoiding AI hallucinations.
*   **🎭 Emotion & Mood Support**: Choose your current mood (Anxious, Angry, Grieving, etc.), and the AI adapts its tone to be your compassionate companion.
*   **🌍 Multilingual Guidance**: Seamlessly chat in **English** or **Hindi**.
*   **🌓 Divine UI**: A premium, spiritually-themed interface featuring:
    *   **Day/Night Modes**: Switch between a solar-themed light mode and a cosmic dark mode.
    *   **Animated Backgrounds**: Subtle breathing and floating particle effects for a meditative experience.
    *   **Responsive Pill Design**: A modern, clean input area and message bubbles.
*   **🛡️ Safety Layer**: Built-in protection to detect crisis-related inputs and provide supportive resources.

---

## 🏗️ Architecture

The system uses a **RAG (Retrieval-Augmented Generation)** flow optimized for zero-cost performance:

1.  **Frontend (Next.js 15)**: A sleek Single Page Application (SPA) using React Server Components and client-side transitions.
2.  **Backend (FastAPI)**: A high-performance Python API that handles orchestration.
3.  **Vector Search**: Uses `SentenceTransformers` (`BAAI/bge-small-en-v1.5`) for in-memory semantic retrieval—no heavy database required for free-tier deployments.
4.  **LLM Inference**: Powered by **Groq** (Llama 3.1 8B) for near-instant response times.

---

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+** & **npm**
- **Python 3.10+**
- **Groq API Key** (Get it free at [console.groq.com](https://console.groq.com))

### 1. Project Setup
```bash
git clone https://github.com/yourusername/GitaGuideAI.git
cd GitaGuideAI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac 
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to begin your journey.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Next.js, React, Lucide Icons, Vanilla CSS (Premium Custom Styles) |
| **Backend** | FastAPI, Pydantic, SlowAPI (Rate Limiting) |
| **AI/ML** | Groq API, LangDetect, Sentence-Transformers (Embeddings) |
| **Data** | 701 Verses of the Bhagavad Gita (Public Domain) |

---

## 📜 Legal & Safety

- **Data Source**: This AI uses public domain translations of the Bhagavad Gita (*Edwin Arnold, Annie Besant*).
- **Not Professional Advice**: GitaGuide AI is for philosophical and spiritual reflection. It **does not** provide medical, legal, or financial advice.
- **Safety**: If a user indicates self-harm, the system is designed to provide immediate support resources (e.g., 988 Suicide & Crisis Lifeline).

---

*“Change is the law of the universe. You can be a millionaire, or a pauper in an instant.”* — **The Bhagavad Gita**

Built with ❤️ and Dharma.
