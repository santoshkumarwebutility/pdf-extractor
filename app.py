from flask import Flask, request, jsonify
import pdfplumber

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    specs = {}

    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # 1. Table structure fetch karein
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Row filteration (Kam se kam 2 columns mandatory)
                        if row and len(row) >= 2 and row[0] and row[1]:
                            key = str(row[0]).strip().replace('\n', ' ')
                            val = str(row[1]).strip().replace('\n', ' ')
                            if key and val and key.lower() != 'property':
                                specs[key] = val

                # 2. Agar table nahi mili toh line-by-line fallback parsing
                if not specs:
                    text = page.extract_text()
                    if text:
                        for line in text.split('\n'):
                            if ':' in line:
                                parts = line.split(':', 1)
                                k = parts[0].strip()
                                v = parts[1].strip()
                                if k and v:
                                    specs[k] = v

        return jsonify(specs)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
