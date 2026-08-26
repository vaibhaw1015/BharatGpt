from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from groq import Groq
import os
from dotenv import load_dotenv
import pandas as pd
import glob
import traceback

import google.generativeai as genai # Keeping for now as the transition to google-genai is a major change, but fixing the warning by suppressing or using current best practice.

# Load environment variables
load_dotenv()

app = FastAPI(title="Bharat GPT API", description="AI Assistant for Indian Agriculture")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request Logger for Debugging
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"  [DEBUG] Incoming {request.method} request to {request.url.path}")
    response = await call_next(request)
    print(f"  [DEBUG] Response Status: {response.status_code}")
    return response

# Set up API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize Clients
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"  [ERR] Failed to initialize Groq: {e}")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"  [ERR] Failed to initialize Gemini: {e}")
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
xlsx_files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))
data_files = csv_files + xlsx_files

# Build a concise agricultural context
agricultural_context = """You are Bharat GPT, an advanced AI agricultural expert specifically trained for Indian farming conditions. 
You provide expert advice on crops, rainfall, soil types, climate, and farming practices across India.
You speak in a friendly, helpful manner and give actionable advice to Indian farmers.
When recommending crops, consider soil nutrients (N, P, K), temperature, humidity, pH, and rainfall.
Always provide practical, region-specific advice based on the data you have been given.
If you don't know the answer, suggest consulting a local KVK (Krishi Vigyan Kendra).
"""

print(f"\n--- Loading {len(data_files)} dataset files ---")

if data_files:
    agricultural_context += "\n\nAvailable Agricultural Data Context:\n"
    for file in data_files:
        try:
            filename = os.path.basename(file)
            if file.endswith('.csv'):
                df = pd.read_csv(file, nrows=30) # Reduced nrows for prompt efficiency
                total_rows = "Check dataset for details" 
            elif file.endswith('.xlsx'):
                df = pd.read_excel(file, nrows=30)
                total_rows = "Check dataset for details"

            agricultural_context += f"\n--- Dataset: {filename} ---\n"
            agricultural_context += f"Columns: {', '.join(df.columns.tolist())}\n"
            agricultural_context += f"Key Data Samples:\n{df.head(3).to_csv(index=False)}\n"
            
            print(f"  [OK] Loaded: {filename}")

        except Exception as e:
            print(f"  [ERR] Error loading {file}: {e}")
else:
    agricultural_context += "\n\nNote: No dataset files were found in the data folder."

# Trim context if too long
MAX_CONTEXT_CHARS = 10000
if len(agricultural_context) > MAX_CONTEXT_CHARS:
    agricultural_context = agricultural_context[:MAX_CONTEXT_CHARS] + "\n...(data truncated)"

class QueryRequest(BaseModel):
    query: str
    image_base64: str = None

class QueryResponse(BaseModel):
    answer: str
    model_used: str

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "datasets_loaded": len(data_files), 
        "gemini_active": bool(GEMINI_API_KEY),
        "groq_active": bool(GROQ_API_KEY)
    }

async def chat_with_gemini(query: str, image_base64: str = None):
    if not GEMINI_API_KEY:
        raise Exception("Gemini API Key missing")
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt_parts = [agricultural_context, f"\nUser Query: {query}"]
    
    if image_base64:
        import base64
        image_data = base64.b64decode(image_base64)
        img = {"mime_type": "image/jpeg", "data": image_data}
        response = model.generate_content([agricultural_context, query, img])
    else:
        response = model.generate_content(prompt_parts)
    
    return response.text

async def chat_with_groq(query: str, image_base64: str = None):
    if not groq_client:
        raise Exception("Groq client not initialized")
    
    if image_base64:
        model_to_use = "llama-3.2-11b-vision-preview"
        user_content = [
            {"type": "text", "text": query},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
    else:
        model_to_use = "openai/gpt-oss-20b"
        user_content = query

    completion = groq_client.chat.completions.create(
        model=model_to_use,
        messages=[
            {"role": "system", "content": agricultural_context},
            {"role": "user", "content": user_content}
        ],
        temperature=0.5,
        max_tokens=1024,
    )
    return completion.choices[0].message.content

@app.post("/api/chat", response_model=QueryResponse)
async def chat_handler(request: QueryRequest):
    errors = []
    
    # Try Gemini First
    if GEMINI_API_KEY:
        try:
            print(f"  [CHAT] Attempting Gemini...")
            answer = await chat_with_gemini(request.query, request.image_base64)
            return QueryResponse(answer=answer, model_used="Bharat GPT v1.1")
        except Exception as e:
            errors.append(f"Gemini error: {str(e)}")
            print(f"  [WARN] Gemini failed: {e}")

    # Fallback to Groq
    if groq_client:
        try:
            print(f"  [CHAT] Attempting Groq fallback...")
            answer = await chat_with_groq(request.query, request.image_base64)
            return QueryResponse(answer=answer, model_used="Bharat GPT v1.1")
        except Exception as e:
            errors.append(f"Groq error: {str(e)}")
            print(f"  [WARN] Groq failed: {e}")

    # If both failed or neither configured
    error_summary = " | ".join(errors) if errors else "No AI models configured. Please check your .env file."
    return QueryResponse(answer=f"Bharat GPT Error: {error_summary}", model_used="None")

# Diagnostic: Print paths to logs during startup
print(f"--- Production Path Audit ---")
print(f"BASE_DIR: {BASE_DIR}")
print(f"FRONTEND_DIR: {FRONTEND_DIR}")
print(f"Index exists: {os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))}")
print(f"-----------------------------")

# Mount static files (css, js, images) last
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# Force Redeploy - Branding Update
