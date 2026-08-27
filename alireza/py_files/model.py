import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

gapgpt_base_url = os.getenv("GAPGPT_BASE_URL")
gapgpt_api_key = os.getenv("GAPGPT_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

gpt_luna = ChatOpenAI(
    model="gpt-5.6-luna", base_url=gapgpt_base_url, api_key=gapgpt_api_key
)

gpt_terra = ChatOpenAI(
    model="gpt-5.6-terra", base_url=gapgpt_base_url, api_key=gapgpt_api_key
)

claude_sonnet = ChatOpenAI(
    model="claude-sonnet-5", base_url=gapgpt_base_url, api_key=gapgpt_api_key
)

claude_opus = ChatOpenAI(
    model="claude-opus-5", base_url=gapgpt_base_url, api_key=gapgpt_api_key
)

gemini_flashlite = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite", api_key=google_api_key
)

gemini_flash = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash", api_key=google_api_key
)
