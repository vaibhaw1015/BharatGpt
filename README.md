# BharatGPT 🌾

BharatGPT is an AI-powered agricultural advisory system designed to provide farmers with localized and data-driven recommendations for Indian agriculture.

## 🚀 Live Demo

https://bharatgpt-tbaq.onrender.com

## 📌 Overview

BharatGPT combines Large Language Models with domain-specific agricultural datasets to provide useful guidance related to crops, soil, weather, rainfall, and agricultural conditions across India.

The system uses a Retrieval-Augmented Generation (RAG) approach to provide responses grounded in relevant agricultural data.

## ✨ Features

- 🌾 AI-powered agricultural advisory
- 🌱 Soil and crop-based recommendations
- 🌦️ Weather and rainfall-aware guidance
- 🇮🇳 Designed specifically for Indian agriculture
- 📊 Uses domain-specific agricultural datasets
- 🤖 Powered by Groq API
- 🔍 Retrieval-Augmented Generation (RAG) pipeline
- 💬 Natural-language interaction
- 🖼️ Support for image-based agricultural queries
- ⚡ Fast AI responses

## 🧠 AI & RAG Architecture

BharatGPT uses a Retrieval-Augmented Generation pipeline that combines:

- Soil data
- Crop recommendation datasets
- Weather information
- Rainfall and climate-related data
- Location information
- Agricultural domain knowledge

Relevant agricultural information is provided as context to the AI model before generating the response.

This helps improve the relevance and accuracy of recommendations compared with relying only on the language model's general knowledge.

## 🛠️ Tech Stack

### Backend

- Python
- FastAPI
- Groq API
- Pandas
- Pydantic
- Uvicorn

### AI

- Groq LLM API
- Retrieval-Augmented Generation (RAG)
- Domain-specific agricultural datasets

### Frontend

- HTML
- CSS
- JavaScript

### Deployment

- Render

## 📂 Project Structure

```text
BharatGpt/
│
├── backend/
│   └── main.py
│
├── data/
│   ├── Crop_recommendation.csv
│   ├── ICRISAT-District Level Data.csv
│   ├── Air quality information.xlsx
│   ├── Astronomical.xlsx
│   ├── Location information.xlsx
│   └── Weather data.xlsx
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── requirements.txt
├── Procfile
├── .gitignore
└── README.md
