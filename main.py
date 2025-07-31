    from flask import Flask, request, jsonify
    from utils.extract_pdf import extract_pdf
    import os

    app = Flask(__name__)

    # Buat folder output kalau belum ada
    os.makedirs("output", exist_ok=True)

    @app.route('/')
    def index():
        return "📄 PDF Extractor API is running."

    @app.route('/upload', methods=['POST'])
    def upload_pdf():
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file:
            filepath = os.path.join("output", file.filename)
            file.save(filepath)

            # Ekstrak PDF + OCR + Markdown tabel
            try:
                output_text = extract_pdf(filepath)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

            # Simpan hasil ke file
            output_path = os.path.join("output", "full_text_cleaned.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_text)

            return jsonify({
                "message": "Extracted successfully",
                "text": output_text
            }), 200

        return jsonify({"error": "Unknown error"}), 500

    if __name__ == '__main__':
        port = int(os.environ.get("PORT", 8000))  # ⚠️ WAJIB untuk Railway
        app.run(host='0.0.0.0', port=port)