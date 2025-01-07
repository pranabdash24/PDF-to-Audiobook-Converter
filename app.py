import streamlit as st
from PyPDF2 import PdfReader
from gtts import gTTS
import pyttsx3
from io import BytesIO
import os
import time

# Set the page configuration (must be the first Streamlit command)
st.set_page_config(page_title="PDF to Audiobook Converter", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
        /* General Page Styles */
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f7fa;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            text-transform: uppercase;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .stSidebar {
            background-color: #f5f7fa;
        }
        footer {
            text-align: center;
            font-size: 0.8rem;
        }
        footer a {
            color: #007BFF;
            text-decoration: none;
        }
    </style>
""", unsafe_allow_html=True)

# Application title
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🎧 PDF to Audiobook Converter</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center;'>Transform your PDFs into high-quality audiobooks with ease!</p>", unsafe_allow_html=True)

# Sidebar for customization options
st.sidebar.header("📊 Customization Settings")
tts_method = st.sidebar.selectbox(
    "TTS Method", ["Online (gTTS)", "Offline (pyttsx3)"], index=0
)
language = st.sidebar.selectbox(
    "Language/Accent", ["English (US)", "English (UK)", "English (AU)"], index=0
)
gender = st.sidebar.radio("Voice Gender (Offline Only)", ["Male", "Female"], index=0)
speed = st.sidebar.slider("Speech Speed", 0.5, 2.0, 1.0, step=0.1)

# Input method
st.sidebar.header("📂 Input Method")
input_method = st.sidebar.radio("Choose Method", ["Upload PDF File", "Paste Text"])

# Input Section
if input_method == "Upload PDF File":
    uploaded_file = st.file_uploader("Upload your PDF file below:", type="pdf")
    extracted_text = ""
    if uploaded_file:
        try:
            pdf_reader = PdfReader(uploaded_file)
            extracted_text = "".join(page.extract_text() for page in pdf_reader.pages)
            if not extracted_text.strip():
                st.error("No text could be extracted from the uploaded PDF. Please try another file.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {str(e)}")
else:
    extracted_text = st.text_area("Paste your text below:", height=300)

if extracted_text.strip():
    st.markdown("### 📝 Extracted Text")
    st.text_area("Extracted Text", extracted_text, height=300)

    # Generate audio button
    if st.button("Generate Audiobook"):
        st.info("Generating audio... Please wait.")
        progress = st.progress(0)
        audio_buffer = BytesIO()

        if tts_method == "Online (gTTS)":
            lang_map = {"English (US)": "en", "English (UK)": "en-uk", "English (AU)": "en-au"}
            selected_lang = lang_map.get(language, "en")

            for i in range(1, 51):
                progress.progress(i * 2)
                time.sleep(0.02)

            try:
                tts = gTTS(text=extracted_text, lang=selected_lang, slow=(speed < 1.0))
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                for i in range(51, 101):
                    progress.progress(i)
                    time.sleep(0.02)
            except Exception as e:
                st.error(f"An error occurred during audio generation: {str(e)}")
                progress.progress(0)

        elif tts_method == "Offline (pyttsx3)":
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            selected_voice = voices[0].id if gender == "Male" else voices[1].id
            engine.setProperty('voice', selected_voice)
            engine.setProperty('rate', int(speed * 150))

            temp_file = "audiobook.mp3"
            for i in range(1, 31):
                progress.progress(i * 3)
                time.sleep(0.02)

            try:
                engine.save_to_file(extracted_text, temp_file)
                engine.runAndWait()
                with open(temp_file, "rb") as f:
                    audio_buffer.write(f.read())
                audio_buffer.seek(0)
                os.remove(temp_file)
                for i in range(31, 101):
                    progress.progress(i)
                    time.sleep(0.02)
            except Exception as e:
                st.error(f"An error occurred during audio generation: {str(e)}")
                progress.progress(0)

        st.audio(audio_buffer, format="audio/mp3", start_time=0)
        st.success("Audio generation complete!")
        st.download_button(
            label="🔽 Download Audiobook",
            data=audio_buffer,
            file_name="audiobook.mp3",
            mime="audio/mp3",
        )
else:
    st.info("Please upload a file or paste text to start.")

# Footer
st.markdown("---")
st.markdown(
    """
    <footer>
        Made with ❤️ by Pranab 🚀 | 
        <a href="https://www.streamlit.io" target="_blank">Powered by Streamlit</a>
    </footer>
    """,
    unsafe_allow_html=True
)
