import os
import uuid
import fitz
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "PDF Table Extract API Running"


@app.route("/extract", methods=["POST"])
def extract_pdf():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # unique temp file
    filename = f"{uuid.uuid4()}.pdf"
    file.save(filename)

    try:
        doc = fitz.open(filename)
        table_results = []

        for page_number, page in enumerate(doc, start=1):

            tables = page.find_tables()

            # Skip page if no tables
            if not tables:
                continue

            for table in tables:
                data = table.extract()

                if not data or len(data) < 2:
                    continue

                headers = data[0]
                rows = data[1:]

                for row in rows:
                    row_data = {
                        "page": page_number
                    }

                    for i in range(len(headers)):
                        header = headers[i] if headers[i] else f"column_{i}"
                        value = row[i] if i < len(row) else ""

                        row_data[header.strip()] = (
                            value.strip() if value else ""
                        )

                    table_results.append(row_data)

        doc.close()
        os.remove(filename)

        return jsonify({
            "total_rows": len(table_results),
            "tables": table_results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
