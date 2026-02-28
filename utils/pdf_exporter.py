from fpdf import FPDF
import re


def strip_markdown(text: str) -> str:
    text = text.replace("—", "-")
    text = text.replace("–", "-")
    text = text.replace("\u2014", "-")
    text = text.replace("\u2013", "-")
    text = text.replace('"', '"')
    text = text.replace('"', '"')
    text = text.replace("'", "'")
    text = text.replace("'", "'")
    text = text.replace("…", "...")
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"[-*]\s", "- ", text)
    return text


def safe(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")


def export_to_pdf(transcript: str, outputs: dict) -> bytes:
    pdf = FPDF()
    pdf.set_margins(25, 25, 25)
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    # Calculate usable width
    W = pdf.w - pdf.l_margin - pdf.r_margin

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 30, 60)
    pdf.cell(W, 12, "LectureAI - Generated Notes", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(W, 8, "Powered by Groq Whisper + OpenRouter", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    # Transcript
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 60)
    pdf.cell(W, 10, "Raw Transcript", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(W, 6, safe(strip_markdown(transcript[:2000])))
    pdf.ln(5)

    # Notes
    if "notes" in outputs:
        pdf.add_page()
        W = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 30, 60)
        pdf.cell(W, 10, "Structured Notes", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(W, 6, safe(strip_markdown(outputs["notes"])))

    # Flashcards
        # Flashcards
        if "flashcards" in outputs:
            pdf.add_page()
            W = pdf.w - pdf.l_margin - pdf.r_margin
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(30, 30, 60)
            pdf.cell(W, 10, "Flashcards", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
            for i, card in enumerate(outputs["flashcards"], 1):
                q = safe(strip_markdown(card.get("question", "")))
                a = safe(strip_markdown(card.get("answer", "")))

                # Question
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(50, 50, 150)
                pdf.set_x(pdf.l_margin)  # Reset X to left margin
                pdf.multi_cell(W, 7, f"Q{i}: {q}")

                # Answer
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(40, 100, 40)
                pdf.set_x(pdf.l_margin)  # Reset X to left margin
                pdf.multi_cell(W, 7, f"A: {a}")
                pdf.ln(4)

    # Glossary
    if "glossary" in outputs:
        pdf.add_page()
        W = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 30, 60)
        pdf.cell(W, 10, "Glossary", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        for term, definition in outputs["glossary"].items():
            t = safe(strip_markdown(term))
            d = safe(strip_markdown(definition))
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(W, 7, t)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(W, 6, f"  {d}")
            pdf.ln(2)

    return bytes(pdf.output())