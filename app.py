import streamlit as st
import whisper
import tempfile
import os
import io
import subprocess
from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY  = os.getenv("GROQ_API_KEY")
GROQ_MODEL    = "llama-3.3-70b-versatile"
WHISPER_SIZE  = "base"
SYSTEM_PROMPT = (
    "Você é um assistente de voz inteligente, amigável e conciso. "
    "Responda sempre no idioma escolhido pelo usuário."
)

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="VoiceAssist", page_icon="🎤", layout="centered")

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background: #0d0d0f; color: #e8e8e8; }

.app-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid #222;
    margin-bottom: 2rem;
}
.app-header h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -1px;
    margin: 0;
}
.app-header .subtitle {
    font-size: 0.85rem;
    color: #555;
    margin-top: 0.4rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.msg-user { display: flex; justify-content: flex-end; margin: 1rem 0; }
.msg-user .bubble {
    background: #1a1a2e;
    border: 1px solid #2d2d5e;
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.2rem;
    max-width: 100%;
    color: #c5c5f0;
    font-size: 0.95rem;
    line-height: 1.5;
}
.msg-assistant { display: flex; justify-content: flex-start; margin: 1rem 0; }
.msg-assistant .bubble {
    background: #111;
    border: 1px solid #2a2a2a;
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.2rem;
    max-width: 75%;
    color: #d4d4d4;
    font-size: 0.95rem;
    line-height: 1.5;
}
.role-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #444;
    margin-bottom: 0.3rem;
}
.transcript-box {
    background: #111;
    border: 1px dashed #2a2a2a;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    color: #888;
    font-style: italic;
    font-size: 0.9rem;
    margin: 1rem 0;
}
section[data-testid="stSidebar"] { background: #0a0a0c; border-right: 1px solid #1a1a1a; }
section[data-testid="stSidebar"] * { color: #aaa !important; }
.stButton > button {
    background: transparent;
    border: 1px solid #333;
    color: #bbb;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 1px;
    transition: all 0.2s;
}
.stButton > button:hover { border-color: #666; color: #fff; background: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>🎤 VoiceAssist</h1>
  <div class="subtitle">Whisper · Groq · gTTS</div>
</div>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = []
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")

    idioma = st.selectbox(
        "Idioma",
        options=["pt", "en", "es", "fr", "de"],
        format_func=lambda x: {
            "pt": "🇧🇷 Português",
            "en": "🇺🇸 English",
            "es": "🇪🇸 Español",
            "fr": "🇫🇷 Français",
            "de": "🇩🇪 Deutsch",
        }[x],
        index=0,
    )

    st.divider()

    if st.button("🗑️ Limpar conversa"):
        st.session_state.chat_history = []
        st.session_state.groq_messages = []
        st.session_state.last_audio_id = None
        st.session_state.input_key += 1
        st.rerun()

    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY não encontrada no .env")

# ─── HELPERS ──────────────────────────────────────────────────────────────────
@st.cache_resource
def load_whisper_model():
    return whisper.load_model(WHISPER_SIZE)


def transcribe_audio(audio_bytes: bytes, lang: str) -> str:
    """
    st.audio_input retorna webm/ogg.
    Converte para wav 16kHz mono via ffmpeg antes do Whisper.
    """
    model = load_whisper_model()

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as src:
        src.write(audio_bytes)
        src_path = src.name

    wav_path = src_path.replace(".webm", ".wav")

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", src_path, "-ar", "16000", "-ac", "1", "-f", "wav", wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        result = model.transcribe(wav_path, language=lang)
        return result["text"].strip()
    finally:
        for p in (src_path, wav_path):
            if os.path.exists(p):
                os.unlink(p)


def ask_groq(messages: list) -> str:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content


def text_to_speech(text: str, lang: str) -> bytes:
    tts = gTTS(text=text, lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def process_and_reply(user_text: str, lang: str):
    if not st.session_state.groq_messages:
        st.session_state.groq_messages.append({"role": "system", "content": SYSTEM_PROMPT})

    st.session_state.groq_messages.append({"role": "user", "content": user_text})
    st.session_state.chat_history.append({"role": "user", "content": user_text})

    with st.spinner("Gerando resposta..."):
        resposta = ask_groq(st.session_state.groq_messages)

    st.session_state.groq_messages.append({"role": "assistant", "content": resposta})

    with st.spinner("Sintetizando voz..."):
        audio_bytes = text_to_speech(resposta, lang)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": resposta, "audio": audio_bytes}
    )
    st.rerun()


def render_chat():
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-user">
              <div>
                <div class="role-label" style="text-align:right">Você</div>
                <div class="bubble">{msg["content"]}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-assistant">
              <div>
                <div class="role-label">Assistente</div>
                <div class="bubble">{msg["content"]}</div>
              </div>
            </div>""", unsafe_allow_html=True)
            if "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
render_chat()

st.divider()

tab_voz, tab_texto = st.tabs(["🎙️ Voz", "⌨️ Texto"])

# ── Aba Voz ────────────────────────────────────────────────────────────────────
with tab_voz:
    st.caption("Grave sua mensagem. O assistente transcreve e responde automaticamente.")
    audio_input = st.audio_input("Clique para gravar")

    if audio_input is not None:
        # Calcula hash para evitar reprocessar o mesmo áudio em reruns
        raw = audio_input.read()
        audio_id = hash(raw)

        if audio_id != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_id

            if not GROQ_API_KEY:
                st.error("GROQ_API_KEY não encontrada no .env")
            else:
                with st.spinner("Transcrevendo com Whisper..."):
                    transcript = transcribe_audio(raw, idioma)

                if transcript:
                    st.markdown(
                        f'<div class="transcript-box">📝 {transcript}</div>',
                        unsafe_allow_html=True,
                    )
                    process_and_reply(transcript, idioma)
                else:
                    st.warning("Não consegui transcrever. Tente falar mais próximo do microfone.")

# ── Aba Texto ──────────────────────────────────────────────────────────────────
with tab_texto:
    st.caption("Prefere digitar? Pode usar por aqui também.")

    col1, col2 = st.columns([5, 1])
    with col1:
        texto_input = st.text_input(
            "Mensagem",
            key=f"texto_{st.session_state.input_key}",
            placeholder="Digite sua mensagem...",
            label_visibility="collapsed",
        )
    with col2:
        enviar = st.button("Enviar", use_container_width=True)

    if (enviar or texto_input) and texto_input:
        if not GROQ_API_KEY:
            st.error("GROQ_API_KEY não encontrada no .env")
        else:
            msg = texto_input
            st.session_state.input_key += 1  # novo key → campo recriado vazio no rerun
            process_and_reply(msg, idioma)