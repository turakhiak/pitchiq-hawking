# PitchIQ

AI-powered pitch deck analysis platform with industry intelligence.

## Features
- 📊 Structured analysis (Company, Market, Financial, Risk)
- 🧠 Industry Intelligence System (4 sectors)
- 💡 Competitive Research Agent
- 📈 Early-stage startup focus
- 🎯 VC-specific metrics

## Tech Stack
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, ChromaDB
- **AI**: Google Gemini

## Deployment
- Frontend: Vercel
- Backend: Railway

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8002
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```
GOOGLE_API_KEY=your_gemini_api_key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8002
```

## Created By
Turak Hiak (turakhiak@gmail.com)
