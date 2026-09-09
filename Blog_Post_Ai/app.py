import os
import random
import urllib.parse
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration (Must be first)
st.set_page_config(
    page_title="BlogCraft AI",
    page_icon="✍️",
    layout="wide"
)

# 2. Safely Load API Key (Check Cloud Secrets first, then Env, then local file)
google_gemini_api_key = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        google_gemini_api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not google_gemini_api_key:
    google_gemini_api_key = os.environ.get("GEMINI_API_KEY")

if not google_gemini_api_key:
    try:
        from apikey import google_gemini_api_key as local_key
        if local_key and "ENTER_YOUR" not in str(local_key):
            google_gemini_api_key = local_key
    except ImportError:
        pass

# 3. Main Header
st.title("✍️ BlogCraft AI — Intelligent Content Generation")
st.subheader("🌐 AI-powered content creation tailored to your niche and audience.")

# 4. Helper: Generate Visual Image Prompt using Gemini
def create_visual_prompt(title: str, keywords: str) -> str:
    client = genai.Client(api_key=google_gemini_api_key)
    
    instruction = f"""
    You are an expert AI prompt engineer for image generators like Midjourney and FLUX.
    Based on the blog title: '{title}' and keywords: '{keywords}', generate ONE highly descriptive, realistic, and cinematic visual scene description.
    
    Rules:
    - Describe concrete objects, realistic lighting, perspective, colors, and environment.
    - DO NOT include abstract text, text overlays, or blog instructions.
    - Return ONLY the image prompt sentence (max 30 words).
    """
    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=instruction,
    )
    return response.text.strip().replace("\n", " ")

# 5. Helper: Pollinations AI URL Generator
def get_pollinations_image_url(prompt: str, width: int = 1024, height: int = 600) -> str:
    seed = random.randint(1, 999999)
    encoded_prompt = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# 6. Helper: Blog Text Generator
def generate_blog_post(title: str, kw: str, count: int):
    client = genai.Client(api_key=google_gemini_api_key)
    model = "gemini-3.5-flash-lite"

    user_prompt = f"""
    Please generate a complete, high-quality blog post with the following requirements:
    - **Blog Title / Topic:** {title}
    - **Target Keywords:** {kw}
    - **Target Word Count:** Approximately {count} words
    """

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="MINIMAL",
        ),
        system_instruction=[
            types.Part.from_text(
                text="""You are an expert content creator and SEO blog writer.
Formatting & Structure Guidelines:
1. Output in clean Markdown format with an H1 main title, H2/H3 section headers, and bullet points where helpful.
2. Begin with an engaging introduction hook.
3. Deliver high-value, actionable sections that seamlessly incorporate the keywords naturally.
4. Conclude with a strong summary and a Call to Action (CTA).
5. Ensure the content is original, informative, and free of repetitive fluff."""
            ),
        ],
    )

    response_stream = client.models.generate_content_stream(
        model=model,
        contents=user_prompt,
        config=generate_content_config,
    )

    for chunk in response_stream:
        if chunk.text:
            yield chunk.text

# 7. Sidebar Inputs
with st.sidebar:
    st.title("Input your Blog Detail")
    st.subheader("Enter the details of the blog you want to generate")

    blog_title = st.text_input("Blog Title", placeholder="e.g. Future of Generative AI")
    keywords = st.text_area("Keywords (comma-separated)", placeholder="e.g. AI, Deep Learning, Automation")
    num_word = st.slider("Number of Words", min_value=250, max_value=1000, step=250, value=500)
    
    submit_button = st.button("Generate Blog", use_container_width=True)

# 8. Main Execution Pipeline
if submit_button:
    if not google_gemini_api_key or "ENTER_YOUR" in str(google_gemini_api_key):
        st.error("❌ Gemini API Key is missing. Please configure `GEMINI_API_KEY` in Streamlit Cloud Secrets.")
    elif not blog_title.strip() or not keywords.strip():
        st.warning("⚠️ Please provide both a Blog Title and Keywords before generating.")
    else:
        st.divider()

        # Step A: Generate and Display 1 Hero Image on Top
        with st.spinner("Designing featured hero image..."):
            try:
                visual_prompt = create_visual_prompt(blog_title, keywords)
                hero_image_url = get_pollinations_image_url(visual_prompt)
                st.image(hero_image_url, caption=f"Hero Visual: {visual_prompt}", use_container_width=True)
            except Exception as e:
                st.error(f"Image generation failed: {e}")

        st.divider()
        
        # Step B: Stream Blog Article Below
        st.subheader(f"📝 Article: {blog_title}")
        with st.spinner("Crafting your blog post..."):
            try:
                st.write_stream(generate_blog_post(blog_title, keywords, num_word))
                st.success("🎉 Blog post and hero visual generated successfully!")
            except Exception as e:
                st.error(f"Text generation failed: {e}")
