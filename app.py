
from flask import Flask, request, jsonify
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def home():
    return "CFO Webhook API is running."

@app.route('/process-cfo', methods=['POST'])
def process_cfo():
    try:
        pos_file = request.files['pos_file']
        upi_file = request.files['upi_file']

        pos_df = pd.read_csv(io.StringIO(pos_file.read().decode('utf-8')))
        upi_df = pd.read_csv(io.StringIO(upi_file.read().decode('utf-8')))

        pos_total = pos_df['Net Amount'].sum() + pos_df['Taxes'].sum()
        upi_total = upi_df['UPI Amount'].astype(float).sum()

        return jsonify({
            "summary": {
                "POS Total": round(pos_total, 2),
                "UPI Total": round(upi_total, 2),
                "Short/Excess": round(upi_total - pos_total, 2)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
