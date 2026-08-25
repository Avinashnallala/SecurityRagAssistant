import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_model():
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        raise ValueError('Groq_Api_key is missing')
    model=ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY,
        temperature=0
    )

    return model