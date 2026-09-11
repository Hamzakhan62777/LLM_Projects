import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()


def get_Gemini_respose(input_text):
    response = requests.post(
        "http://localhost:8000/essay/invoke",
        json={"input": {"topic": input_text}},
    )
    # 'output' is already the raw string returned by StrOutputParser
    return response.json()["output"]

st.title('Langchain Demo With Gemini')
input_text=st.text_input("Write an essay on")


if input_text:
    st.write(get_Gemini_respose(input_text))