import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io
import os

def extract_pdf(filepath):
    hasil_output = []
    pdf_file = fitz.open(filepath)

    for page_number in range(len(pdf_file)):
        hasil_output.append(f"== Halaman {page_number + 1} ==\n")

        page = pdf_file[page_number]
        text = page.get_text().strip()

        if text:
            # Halaman berbasis teks → gunakan pdfplumber
            with pdfplumber.open(filepath) as pdf:
                plumber_page = pdf.pages[page_number]
                teks = plumber_page.extract_text()
                hasil_output.append(teks.strip() if teks else "")

                # Ekstrak tabel
                tables = plumber_page.extract_tables()
                if tables:
                    hasil_output.append("\n== Tabel Ditemukan ==\n")
                    for table in tables:
                        if not table: continue
                        # Buat tabel markdown
                        header = table[0]
                        rows = table[1:]
                        md_table = "| " + " | ".join(header) + " |\n"
                        md_table += "| " + " | ".join(["---"] * len(header)) + " |\n"
                        for row in rows:
                            md_table += "| " + " | ".join(cell if cell else "" for cell in row) + " |\n"
                        hasil_output.append(md_table)
        else:
            # Halaman gambar (OCR)
            images = convert_from_path(filepath, first_page=page_number+1, last_page=page_number+1)
            for img in images:
                # OCR teks
                ocr_text = pytesseract.image_to_string(img, lang='ind')
                hasil_output.append(ocr_text.strip())

                # OCR tabel (kasar – semua teks diubah baris per baris)
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                rows = []
                current_line = []
                prev_top = None

                for i in range(len(ocr_data['text'])):
                    word = ocr_data['text'][i]
                    if not word.strip(): continue
                    top = ocr_data['top'][i]

                    if prev_top is None:
                        prev_top = top

                    if abs(top - prev_top) > 10:
                        rows.append(current_line)
                        current_line = []
                        prev_top = top

                    current_line.append(word)

                if current_line:
                    rows.append(current_line)

                if rows:
                    hasil_output.append("\n== Tabel OCR Detected ==\n")
                    max_cols = max(len(r) for r in rows)
                    md_table = "| " + " | ".join([f"Kol{i+1}" for i in range(max_cols)]) + " |\n"
                    md_table += "| " + " | ".join(["---"] * max_cols) + " |\n"
                    for row in rows:
                        padded = row + [""] * (max_cols - len(row))
                        md_table += "| " + " | ".join(padded) + " |\n"
                    hasil_output.append(md_table)

    return "\n\n".join(hasil_output)