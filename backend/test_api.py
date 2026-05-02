import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
# Use environment variable from .env
# os.environ["GROQ_API_KEY"] = "gsk_..."


from main import chat_with_bharat_gpt, QueryRequest

async def run_test():
    req = QueryRequest(query="What crops are good for red soil in Maharashtra?")
    try:
        response = await chat_with_bharat_gpt(req)
        print("API Response:", response.answer)
    except Exception as e:
        print("Error:", str(e))

asyncio.run(run_test())
