import streamlit as st
from utils.transcriber import transcribe_audio
from utils.notes_generator import (
    generate_notes,
    generate_flashcards,
    generate_quiz,
    generate_glossary
)
from utils.pdf_exporter import export_to_pdf
from utils.audio_processor import preprocess_audio
import tempfile
import os

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LectureAI — Voice to Notes",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
with open("assets/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎙️ LectureAI")
    st.markdown("---")
    st.subheader("⚙️ Settings")

    language = st.selectbox(
        "Lecture Language",
        ["English", "Hindi", "Spanish", "French", "German", "Auto Detect"],
        index=0
    )

    output_formats = st.multiselect(
        "Generate Output",
        ["📝 Structured Notes", "🃏 Flashcards", "📋 MCQ Quiz", "📖 Glossary"],
        default=["📝 Structured Notes", "🃏 Flashcards"]
    )

    subject_hint = st.text_input(
        "Subject Hint (optional)",
        placeholder="e.g. Data Structures, Thermodynamics",
        help="Helps Gemini generate more relevant content"
    )

    st.markdown("---")
    st.caption("Built with Groq Whisper + OpenRouter LLM")

# ─── Main Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <h1>🎙️ Lecture Voice-to-Notes</h1>
    <p>Upload your lecture audio and get structured notes, flashcards, and quizzes instantly using AI.</p>
</div>
""", unsafe_allow_html=True)

# ─── Upload Section ────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload Lecture Audio or Video",
        type=["mp3", "mp4", "wav", "m4a", "ogg", "flac", "webm"],
        help="Supports MP3, MP4, WAV, M4A, OGG, FLAC, WEBM"
    )

with col2:
    st.markdown("### 💡 Tips for Best Accuracy")
    st.info("""
    - Use clear audio with minimal background noise  
    - Keep file under 25MB for faster processing  
    - 5–15 min clips work best for demo  
    - Add a subject hint for better notes  
    """)

# ─── Process Button ────────────────────────────────────────────────────────────
if uploaded_file:
    st.markdown("---")
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.success(f"✅ File uploaded: **{uploaded_file.name}** ({file_size_mb:.1f} MB)")

    if st.button("🚀 Generate Notes", type="primary", use_container_width=True):

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            # Step 1: Preprocess Audio
            with st.spinner("🔧 Preprocessing audio..."):
                processed_path = preprocess_audio(tmp_path)

            # Step 2: Transcribe
            with st.spinner("🎙️ Transcribing with Whisper... (this may take 1-3 minutes)"):
                transcript = transcribe_audio(processed_path, language=language)
                st.session_state["transcript"] = transcript

            # Step 3: Generate Outputs
            outputs = {}
            if "📝 Structured Notes" in output_formats:
                with st.spinner("📝 Generating structured notes with Gemini..."):
                    outputs["notes"] = generate_notes(transcript, subject_hint)

            if "🃏 Flashcards" in output_formats:
                with st.spinner("🃏 Creating flashcards..."):
                    outputs["flashcards"] = generate_flashcards(transcript, subject_hint)

            if "📋 MCQ Quiz" in output_formats:
                with st.spinner("📋 Generating quiz questions..."):
                    outputs["quiz"] = generate_quiz(transcript, subject_hint)

            if "📖 Glossary" in output_formats:
                with st.spinner("📖 Building glossary..."):
                    outputs["glossary"] = generate_glossary(transcript, subject_hint)

            st.session_state["outputs"] = outputs
            st.success("✅ All done! Scroll down to see your results.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        finally:
            os.unlink(tmp_path)
            if 'processed_path' in locals() and processed_path != tmp_path:
                os.unlink(processed_path)

# ─── Display Results ───────────────────────────────────────────────────────────
if "outputs" in st.session_state and "transcript" in st.session_state:
    st.markdown("---")
    st.markdown("## 📊 Results")

    tab_labels = ["🗒️ Transcript"]
    if "notes" in st.session_state["outputs"]:
        tab_labels.append("📝 Notes")
    if "flashcards" in st.session_state["outputs"]:
        tab_labels.append("🃏 Flashcards")
    if "quiz" in st.session_state["outputs"]:
        tab_labels.append("📋 Quiz")
    if "glossary" in st.session_state["outputs"]:
        tab_labels.append("📖 Glossary")

    tabs = st.tabs(tab_labels)
    tab_index = 0

    # Transcript Tab
    with tabs[tab_index]:
        st.markdown("### Raw Transcript")
        st.text_area("", st.session_state["transcript"], height=300)
        st.download_button("⬇️ Download Transcript", st.session_state["transcript"], "transcript.txt")
    tab_index += 1

    # Notes Tab
    if "notes" in st.session_state["outputs"]:
        with tabs[tab_index]:
            st.markdown(st.session_state["outputs"]["notes"])
            st.download_button("⬇️ Download Notes", st.session_state["outputs"]["notes"], "notes.md")
        tab_index += 1

    # Flashcards Tab
    if "flashcards" in st.session_state["outputs"]:
        with tabs[tab_index]:
            flashcards = st.session_state["outputs"]["flashcards"]
            for i, card in enumerate(flashcards):
                with st.expander(f"Card {i+1}: {card['question']}"):
                    st.success(f"**Answer:** {card['answer']}")
        tab_index += 1

    # Quiz Tab
    if "quiz" in st.session_state["outputs"]:
        with tabs[tab_index]:
            quiz = st.session_state["outputs"]["quiz"]
            st.markdown("### Test Yourself!")
            score = 0
            user_answers = {}
            for i, q in enumerate(quiz):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                user_answers[i] = st.radio(
                    "", q["options"], key=f"q_{i}", index=None, label_visibility="collapsed"
                )
            if st.button("✅ Submit Quiz"):
                for i, q in enumerate(quiz):
                    if user_answers[i] == q["answer"]:
                        score += 1
                        st.success(f"Q{i+1}: ✅ Correct!")
                    else:
                        st.error(f"Q{i+1}: ❌ Correct answer: {q['answer']}")
                st.markdown(f"### 🎯 Score: {score}/{len(quiz)}")
        tab_index += 1

    # Glossary Tab
    if "glossary" in st.session_state["outputs"]:
        with tabs[tab_index]:
            glossary = st.session_state["outputs"]["glossary"]
            for term, definition in glossary.items():
                st.markdown(f"**{term}:** {definition}")
        tab_index += 1

    # PDF Export
    st.markdown("---")
    if st.button("📄 Export All as PDF", use_container_width=True):
        with st.spinner("Generating PDF..."):
            pdf_bytes = export_to_pdf(
                st.session_state["transcript"],
                st.session_state["outputs"]
            )
            st.download_button(
                "⬇️ Download PDF",
                pdf_bytes,
                "lecture_notes.pdf",
                mime="application/pdf",
                use_container_width=True
            )
