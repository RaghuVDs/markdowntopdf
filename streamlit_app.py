# markdown_to_pdf_app.py

# requirements.txt might look like:
# streamlit
# markdown
# xhtml2pdf

import streamlit as st
import markdown
from xhtml2pdf import pisa
import io
from datetime import datetime
import logging
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Conversion Function ---

def markdown_to_pdf_bytes(markdown_string: str) -> bytes | None:
    """Converts a Markdown string to PDF bytes using xhtml2pdf."""
    pdf_buffer = io.BytesIO()
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            markdown_string, extensions=['extra', 'smarty', 'fenced_code']
        )

        # Define HTML structure with COMPACT embedded CSS for single-page preference
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                /* --- Global Compact Settings --- */
                body {{
                    font-family: Arial, Helvetica, sans-serif;
                    line-height: 1.2; /* Reduced line height */
                    font-size: 9pt;   /* Reduced base font size */
                    margin: 0.2in;    /* Explicit page margins (adjust if needed) */
                }}
                p {{
                    margin-top: 0;      /* Remove top margin */
                    margin-bottom: 0.08em; /* Very small bottom margin */
                    padding: 0;
                }}
                ul, ol {{
                    padding-left: 18px; /* Slightly reduce indent */
                    margin-top: 0.05em; /* Very small top margin */
                    margin-bottom: 0.1em; /* Reduced bottom margin */
                    padding-top: 0;
                    padding-bottom: 0;
                }}
                li {{
                    margin-top: 0;
                    margin-bottom: 0; /* No space between list items */
                    padding-top: 0;
                    padding-bottom: 0;
                }}

                /* --- Compact Heading Styles --- */
                h1 {{
                    margin-top: 0;
                    margin-bottom: 0.1em; /* Minimal space after H1 */
                    padding-bottom: 0;
                    text-align: center;
                    font-size: 1.6em; /* Slightly Reduced */
                    line-height: 1.2;
                }}

                h2 {{
                    font-size: 1.15em; /* Reduced */
                    margin-top: 0.6em;  /* Significantly Reduced space above section */
                    margin-bottom: 0.1em;/* Reduced space below heading text */
                    padding-bottom: 0.05em;/* Reduced space between text and line */
                    border-bottom: 0.5px solid #ccc; /* Thinner border */
                    line-height: 1.2;
                }}

                h3, h4, h5, h6 {{
                    font-size: 1.0em; /* Reduced */
                    margin-top: 0.4em; /* Reduced */
                    margin-bottom: 0.05em; /* Very small */
                    line-height: 1.2;
                    padding: 0;
                    font-weight: bold;
                }}
                /* --- END Compact Heading Styles --- */

                /* --- Other Element Styles (mostly unchanged unless vertical space is affected) --- */
                code {{
                    background-color: #f0f0f0; padding: 1px 3px; /* Slightly smaller padding */
                    border-radius: 3px; font-family: monospace; font-size: 0.9em;
                }}
                pre {{
                    background-color: #f0f0f0; padding: 5px; /* Reduced padding */
                    border-radius: 4px; overflow-x: auto; font-family: monospace;
                    font-size: 0.85em; /* Slightly smaller code block font */
                    white-space: pre-wrap; word-wrap: break-word;
                    margin-top: 0.3em; margin-bottom: 0.3em; /* Reduced margins */
                }}
                blockquote {{
                    border-left: 2px solid #ccc; /* Thinner border */
                    padding-left: 10px; /* Reduced padding */
                    margin-left: 0; margin-top: 0.3em; margin-bottom: 0.3em; /* Reduced margins */
                    color: #555; font-size: 0.95em;
                }}
                table {{
                    border-collapse: collapse; width: 100%; margin-bottom: 0.5em; /* Reduced margin */
                    border: 1px solid #ddd;
                }}
                th, td {{
                    border: 1px solid #ddd; padding: 4px; /* Reduced padding */
                    text-align: left; font-size: 0.9em; /* Slightly smaller table text */
                }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                img {{ max-width: 100%; height: auto; display: block; margin-top: 0.5em; margin-bottom: 0.5em; }} /* Reduced margins */
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}

                /* Explicit Page Margins (Optional but can help) */
                @page {{
                    margin: 0.2in; /* Adjust overall page margins */
                }}

            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Render HTML to the PDF buffer
        pisa_status = pisa.CreatePDF(
            html_template.encode('utf-8'),
            dest=pdf_buffer,
            encoding='utf-8'
        )

        # Check for errors
        if pisa_status.err:
            logging.error(f"xhtml2pdf Error converting to PDF: {pisa_status.err}")
            return None
        else:
            logging.info("PDF conversion successful (compact styling).")
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()

    except Exception as e:
        logging.error(f"An unexpected error occurred during PDF conversion: {e}", exc_info=True)
        return None


# --- Streamlit Application UI (Remains the same as the previous enhanced version) ---

st.set_page_config(layout="centered")
st.title("📝 Markdown to PDF Converter")
st.caption("Paste your Markdown text (like a resume or notes) below and click Convert.")

# Text area for Markdown input
markdown_input = st.text_area(
    "Markdown Input:",
    height=400,
    placeholder="# Your Name\nyour.email@example.com | LinkedIn URL | Location\n\n## Summary\nYour professional summary...\n\n## Skills\n- Skill 1\n- Skill 2\n\n## Experience\n**Job Title, Company** | Month Year – Present\n- Accomplishment 1\n- Accomplishment 2\n\n## Education\n**Degree, University** | Year"
)

st.markdown("---")

# Button to trigger conversion
convert_button = st.button("Convert to PDF", type="primary")

# Conversion logic
if convert_button:
    if not markdown_input.strip():
        st.warning("⚠️ Please enter some Markdown text in the input area first.")
    else:
        with st.spinner("⚙️ Converting Markdown to PDF (compact style)... Please wait."):
            pdf_bytes = markdown_to_pdf_bytes(markdown_input)

        if pdf_bytes:
            st.success("✅ Conversion Successful!")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"converted_markdown_{timestamp}.pdf"
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=output_filename,
                mime="application/pdf",
            )
        else:
            st.error("❌ PDF Conversion Failed. Check logs if running locally for more details.")