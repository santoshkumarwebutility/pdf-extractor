from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "PDF Extract API Running"

@app.route("/extract", methods=["POST"])
def extract_pdf():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    filepath = "temp.pdf"
    file.save(filepath)

    try:
        doc = fitz.open(filepath)
        results = []

        for page in doc:
            blocks = page.get_text("blocks")

            for block in blocks:
                text = block[4].strip()
                if text:
                    results.append(text)

        doc.close()
        os.remove(filepath)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()