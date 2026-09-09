import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Environment Variable configuration
# The library specifically checks for GOOGLE_API_KEY
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# LangSmith Tracking
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Create Chatbot Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{input}"),
    ]
)

# Streamlit UI framework
st.title("LangChain Demo With Gemini API")
input_text = st.text_input("Search the topic you want")

# Gemini LLM Call
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.7)
output_parser = StrOutputParser()

# Chain pipeline
chain = prompt | llm | output_parser

if input_text:
    # Changed key from 'question' to 'input' to match {input} in prompt
    st.write(chain.invoke({"input": input_text}))