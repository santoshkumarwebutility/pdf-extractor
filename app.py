import os
import uuid
import fitz
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "PDF Property-Value Extract API Running"


@app.route("/extract", methods=["POST"])
def extract_pdf():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    filename = f"{uuid.uuid4()}.pdf"
    file.save(filename)

    try:
        doc = fitz.open(filename)
        property_value_data = {}

        for page in doc:
            tables = page.find_tables()

            for table in tables:
                data = table.extract()

                for row in data:
                    if len(row) >= 2:
                        key = row[0].strip() if row[0] else ""
                        value = row[1].strip() if row[1] else ""

                        # Skip unwanted rows
                        if key.lower() in ["property", "result", ""]:
                            continue

                        property_value_data[key] = value

        doc.close()
        os.remove(filename)

        return jsonify(property_value_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
