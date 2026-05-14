import streamlit as st

st.set_page_config(
    page_title = "Voice Assistant",
    layout = "wide"
)

# Libraries
import os
import time
import pyttsx3
import speech_recognition as sr   # speech to text
from groq import Groq
from dotenv import load_dotenv

# loading the API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# initialize the LLM model
client = Groq(api_key = GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# initialize the speech to text recognizer
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()

recognizer = get_recognizer()

# initialize Text to Speech engine
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"Failed to initialize TTS Engine: {e}")
        return None

def listen_to_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration = 1)
            audio = recognizer.listen(source, phrase_time_limit=10)
        
        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.UnknownValueError:
        return "Sorry, I didn't catch you"
    except sr.RequestError:
        return "Speech service not available"
    except Exception as e:
        return f"Error: {e}"

def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model = MODEL,
            messages = messages,
            temperature= 0.7
        )
        result = response.choices[0].message.content   # getting 0th reply from the LLM
        return result.strip() if result else "Sorry, I could not generate a response"
    except Exception as e:
        return f"Error getting AI response: {e}"

def speak(text, voice_gender = 'girl'):
    try:
        engine = get_tts_engine()
        if engine is None:
            return
        
        # selecting the voice for the engine
        voices = engine.getProperty("voices")
        if voices:
            if voice_gender == "boy":
                for voice in voices:
                    if "male" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            else:
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break

        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"TTS Error {e}")

def main():
    st.title("codegnan Voice Assistant")
    st.markdown("---")

    # Initialize the chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role" : "system", "content": "You are a helpful voice assistant. Reply just one line"}
        ]
    
    # initialize the messages to display on screen
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # sidebar control panel
    with st.sidebar:
        st.header("CONTROLS")
        tts_enabled = st.checkbox("Enable Text to Speech",value = True)

        # voice gender selection
        voice_gender = st.selectbox(
            "Voice Gender",
            options = ["girl", "boy"],
            index = 0,
            help = "Choose the Voice assistant Voice: Girl or Boy"
            )
        if st.button("Start Voice  Input", type ="primary",use_container_width= True):
            with st.spinner("Listening..."):
                user_input = listen_to_speech()
                
                # if input is not empty and don't have any error
                if user_input and user_input not in ["Sorry, I didn't catch you","Speech service not available"]:
                    st.session_state.messages.append({"role": "user", "content" : user_input})  # used to display chat on screen
                    st.session_state.chat_history.append({"role": "user", "content" : user_input}) # use to pass to LLM

                    # Get the reply from LLM
                    with st.spinner("Thinking..."):
                        ai_response = get_ai_response(st.session_state.chat_history)
                        st.session_state.messages.append({"role": "assistant", "content" : ai_response})  # used to display chat on screen
                        st.session_state.chat_history.append({"role": "assistant", "content" : ai_response}) # use to pass to LLM

                    if tts_enabled:
                        speak(ai_response, voice_gender )

                    st.rerun()
        
        st.markdown("---")

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = [
            {"role" : "system", "content": "You are a helpful voice assistant. Reply just one line"}
        ]
            st.rerun()

    st.subheader("CONVERSATION")
    if not st.session_state.messages:
        st.info("Welcome to Baby Siri : Click on voice button to start")
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])    
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    st.markdown("---")
    st.markdown(
        """
            <div style = 'text-align: center; color: #666;'>
                <p> CopyRight @ sairam
            </div>
        """,
        unsafe_allow_html=True
    )




if __name__ == "__main__":
    main()