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
        # Get uploaded files
        pos_file = request.files.get('pos_file')
        upi_file = request.files.get('upi_file')
        screenshot_file = request.files.get('screenshot_file')
        event_dsr_file = request.files.get('event_dsr_file')

        # Check required files
        if not pos_file or not upi_file or not screenshot_file or not event_dsr_file:
            return jsonify({
                "status": "error",
                "message": "One or more required files are missing: pos_file, upi_file, screenshot_file, event_dsr_file."
            }), 400

        # Read CSVs
        pos_df = pd.read_csv(io.StringIO(pos_file.read().decode('utf-8')))
        upi_df = pd.read_csv(io.StringIO(upi_file.read().decode('utf-8')))

        # Read Excel file
        event_dsr_df = pd.read_excel(event_dsr_file)

        # Screenshot is binary, so just show we received it
        screenshot_name = screenshot_file.filename

        # Dummy sample summary for now (to be replaced with full logic)
        summary = {
            "POS Rows": len(pos_df),
            "UPI Transactions": len(upi_df),
            "Event Rows": len(event_dsr_df),
            "Screenshot Filename": screenshot_name
        }

        return jsonify({
            "status": "success",
            "summary": summary
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

