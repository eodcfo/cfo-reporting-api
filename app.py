from flask import Flask, request, jsonify
import pandas as pd
import io
import traceback

app = Flask(__name__)

@app.route('/')
def home():
    return "CFO Webhook API is running."

def classify_pos_item(row):
    try:
        item = str(row.get("Item Name", "")).lower()
        counter = str(row.get("Counter Name", "")).lower()
        branch = str(row.get("Branch Name", "")).lower()
        created_by = str(row.get("Created By", "")).lower()

        fnb_items = [
            "just milk", "veg sandwiches", "veg pizza", "veg pasta",
            "masala chai", "hot coffee", "water bottle", "coke", "sprite", "fanta", "tea"
        ]

        annual_pass_items = [
            "annual pass", "kids annual pass", "annual pass one time",
            "annual pass unlimited", "kids annual pass one time",
            "annual pass full on masti", "annual pass (kids)", "annual pass entry"
        ]

        games_counters = [
            "jump n fun", "p&h", "boating", "vr games", "e-o-d gun shooting",
            "carnival event", "carnival games"
        ]

        fnb_counters = [
            "momo kiosk", "softy corner", "eod maggi", "dhinchak dhaba",
            "ice cream parlour & kart", "dhinchak nukkad", "snow pops n more",
            "buffet & events", "trampoline cafe", "tea stall", "dhinchak by the lake"
        ]

        if any(ap in item for ap in annual_pass_items):
            return "Annual Pass"

        if counter in games_counters or branch in games_counters:
            return "Games"

        if counter in fnb_counters or branch in fnb_counters:
            return "F&B"

        if any(fnb in item for fnb in fnb_items):
            if created_by in ["heena cashier 1", "heena cashier 2", "heena cashier 3", "heena cashier 4", "heena cashier 5"]:
                return "F&B"

        if branch == "every other day at dme":
            return "Gate DME"

        if branch == "eod":
            return "Gate MV"

        return "Unclassified"

    except Exception as e:
        print("Error in classify_pos_item:", e)
        traceback.print_exc()
        return "Unclassified"

@app.route('/process-cfo', methods=['POST'])
def process_cfo():
    try:
        pos_file = request.files.get('pos_file')
        upi_file = request.files.get('upi_file')
        screenshot_file = request.files.get('screenshot_file')
        event_dsr_file = request.files.get('event_dsr_file')

        if not all([pos_file, upi_file, screenshot_file, event_dsr_file]):
            return jsonify({
                "status": "error",
                "message": "One or more required files are missing: pos_file, upi_file, screenshot_file, event_dsr_file."
            }), 400

        pos_df = pd.read_csv(io.StringIO(pos_file.read().decode('utf-8')))
        upi_df = pd.read_csv(io.StringIO(upi_file.read().decode('utf-8')))

        event_dsr_df = pd.read_excel(event_dsr_file, engine='openpyxl')

        # Classify POS rows
        pos_df['Category'] = pos_df.apply(classify_pos_item, axis=1)

        # Summary for demo purposes
        summary = {
            "POS Rows": len(pos_df),
            "UPI Transactions": len(upi_df),
            "Event Rows": len(event_dsr_df),
            "Screenshot Filename": screenshot_file.filename
        }

        return jsonify({"status": "success", "summary": summary})

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
