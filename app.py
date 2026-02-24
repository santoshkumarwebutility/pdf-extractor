import os
import fitz  # PyMuPDF
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "message": "PDF Table Extractor API",
        "endpoint": "/extract (POST)"
    })


@app.route("/extract", methods=["POST"])
def extract_pdf():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filepath = "temp.pdf"
    file.save(filepath)

    try:
        doc = fitz.open(filepath)
        all_tables = []

        for page_number, page in enumerate(doc, start=1):

            tables = page.find_tables()

            for table in tables:
                data = table.extract()

                if len(data) > 1:
                    headers = data[0]
                    rows = data[1:]

                    for row in rows:
                        row_dict = {"page": page_number}

                        for i in range(len(headers)):
                            header = headers[i] if headers[i] else f"column_{i}"
                            value = row[i] if i < len(row) else ""

                            row_dict[header.strip()] = (
                                value.strip() if value else ""
                            )

                        all_tables.append(row_dict)

        doc.close()
        os.remove(filepath)

        return jsonify({
            "total_rows": len(all_tables),
            "data": all_tables
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
