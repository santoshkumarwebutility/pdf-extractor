from flask import Flask, request, jsonify
import fitz
import os
import uuid

app = Flask(__name__)

@app.route("/")
def home():
    return "PDF Table Extract API Running"


@app.route("/extract", methods=["POST"])
def extract_pdf():

    if "file" not in request.files:
        return jsonify([])

    file = request.files["file"]
    filename = f"{uuid.uuid4()}.pdf"
    file.save(filename)

    results = []

    try:
        doc = fitz.open(filename)

        for page in doc:

            words = page.get_text("words")
            words.sort(key=lambda w: (w[1], w[0]))  # sort by y then x

            rows = {}

            for w in words:
                y = round(w[1], 0)
                text = w[4]

                if y not in rows:
                    rows[y] = []

                rows[y].append((w[0], text))

            for y in rows:
                line = sorted(rows[y], key=lambda x: x[0])
                texts = [t[1] for t in line]

                if len(texts) >= 2:
                    property_text = texts[0]
                    value_text = " ".join(texts[1:])

                    results.append({
                        "property": property_text.strip(),
                        "value": value_text.strip()
                    })

        doc.close()
        os.remove(filename)

        return jsonify(results)

    except Exception as e:
        return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
