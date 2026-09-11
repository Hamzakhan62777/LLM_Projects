import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langserve import add_routes
from langchain_core.output_parsers import StrOutputParser
import uvicorn

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Gemini_Projects")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A Simple API Server powered by Gemini and LangServe",
)

# 1. Instantiate the Gemini LLM with a specific model
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
# 2. Direct LLM route (raw model access)
add_routes(
    app,
    model,
    path="/gemini",
)

# 3. Prompt Template + Model Chain route
prompt = ChatPromptTemplate.from_template("Write me an essay about {topic} with 100 words")
chain = prompt | model |StrOutputParser()

add_routes(
    app,
    chain,
    path="/essay",
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
