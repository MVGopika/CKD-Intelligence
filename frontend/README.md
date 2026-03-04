# CKD Intelligence Frontend

Next.js frontend for the CKD Intelligence platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your backend URL
```

3. Run development server:
```bash
npm run dev
```

Visit http://localhost:3000

## Features

- Patient Dashboard
- Doctor Dashboard
- Voice Consultation (Web Speech API)
- Clinical Data Input
- eGFR Prediction with SHAP
- Medical Reports Download
- Real-time Charts (Recharts)

## Tech Stack

- Next.js 16
- TypeScript
- Tailwind CSS
- Axios
- Recharts
- Web Speech API

## Project Structure

```
app/              # Next.js pages (App Router)
components/       # Reusable components
lib/              # Utilities and API setup
services/         # API service wrappers
hooks/            # Custom React hooks
types/            # TypeScript type definitions
```

## API Integration

All API calls go through the centralized `lib/api.ts` which handles:
- Authentication tokens
- Request/response interceptors
- Error handling
- Base URL configuration

## Authentication

JWT tokens are stored in localStorage and automatically attached to all API requests via axios interceptors.
