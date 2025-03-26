from flask import Flask, request, jsonify
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def home():
    return "CFO Webhook API is running."

# Classification Logic
def classify_pos_item(row):
    try:
        item_name = str(row.get('Item Name', '')).lower().strip()
        counter = str(row.get('Created By', '')).lower().strip()
        branch = str(row.get('Branch Name', '')).lower().strip()

        # Define classification categories
        fnb_items = [
            "just milk", "veg sandwich", "veg pizza", "veg pasta",
            "masala chai", "hot coffee", "water bottle", "coke",
            "sprite", "fanta", "tea", "lunch coupon", "buffet"
        ]

        annual_pass_items = [
            "annual pass", "kids annual pass", "annual pass one time",
            "annual pass unlimited", "kids annual pass one time",
            "annual pass entry", "annual pass (kids)", "annual pass full on masti"
        ]

        fnb_counters = [
            "momo kiosk", "softy corner", "eod maggi", "dhinchak dhaba",
            "ice cream parlour & kart", "dhinchak by the lake",
            "dhinchak nukkad", "snow pops n more", "buffet & events",
            "tea stall", "trampoline cafe"
        ]

        game_counters = [
            "jump n fun", "p&h", "boating", "vr games",
            "e-o-d gun shooting", "carnival event", "carnival games"
        ]

        # Clean inputs
        clean_item = item_name.replace(" ", "")
        clean_counter = counter.replace(" ", "")

        # Matching Logic
        if any(item in item_name for item in fnb_items):
            return "F&B Revenue"

        if any(pass_item in item_name for pass_item in annual_pass_items):
            return "Annual Pass Revenue"

        if branch == "every other day at dme":
            return "Gate Revenue (DME)"

        if branch == "eod":
            if counter.startswith("tc-"):
                return "Gate Revenue (MV)"

        if branch in fnb_counters:
            return "F&B Revenue"

        if branch in game_counters:
            return "Park Games Revenue"

        if "locker charges" in item_name:
            return "Gate Revenue (MV)"

        return "Unclassified"

    except Exception as e:
        return "Unclassified"

@app.route('/process-cfo', methods=['POST'])
def process_cfo():
    try:
        pos_file = request.files['pos_file']
        upi_file = request.files['upi_file']
        screenshot_file = request.files['screenshot_file']
        event_dsr_file = request.files['event_dsr_file']

        pos_df = pd.read_csv(io.StringIO(pos_file.read().decode('utf-8')))
        upi_df = pd.read_csv(io.StringIO(upi_file.read().decode('utf-8')))
        # Screenshot and DSR file handling can be expanded

        # Apply classification
        pos_df['Category'] = pos_df.apply(classify_pos_item, axis=1)

        # Revenue Summary
        revenue_summary = pos_df.groupby('Category')['Net Amount'].sum().to_dict()

        return jsonify({
            "status": "success",
            "summary": {
                "POS Rows": len(pos_df),
                "UPI Transactions": len(upi_df),
                "Event Rows": 2,  # Placeholder
                "Screenshot Filename": screenshot_file.filename,
                "Revenue Breakdown": revenue_summary
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

