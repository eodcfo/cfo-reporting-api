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

# --- POS Classification Logic ---

def classify_pos_item(row):
    try:
        item = str(row.get('Item Name', '')).lower()
        counter = str(row.get('Counter Name', '')).lower()
        branch = str(row.get('Branch Name', '')).lower()
        created_by = str(row.get('Created By', '')).lower()

        fnb_counters = [
            "momo kiosk", "softy corner", "eod maggi", "dhinchak dhaba",
            "ice cream parlour & kart", "dhinchak nukkad", "snow pops n more",
            "buffet & events", "trampoline cafe", "tea stall", "dhinchak by the lake"
        ]

        park_games_counters = [
            "jump n fun", "p&h", "boating", "vr games", "e-o-d gun shooting",
            "carnival event", "carnival games"
        ]

        annual_pass_items = [
            "annual pass", "annual pass (kids)", "annual pass full on masti",
            "annual pass entry"
        ]

        fnb_items = [
            "just milk", "veg sandwich", "veg pizza", "veg pasta", "masala chai", "hot coffee"
        ]

        if branch == "eod":
            if item in annual_pass_items:
                return "Annual Pass"
            elif counter in ["tc-1", "tc-2", "tc-3", "tc-4", "tc-5"]:
                if item in fnb_items:
                    return "F&B"
                else:
                    return "Gate Revenue (MV)"
            elif counter in fnb_counters:
                return "F&B"
        elif branch == "every other day at dme":
            return "Gate Revenue (DME)"
        elif branch in fnb_counters:
            return "F&B"
        elif branch in park_games_counters:
            return "Park Games"

        return "Unclassified"

    except Exception as e:
        return "Unclassified"

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

