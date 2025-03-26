from flask import Flask, request, jsonify
import pandas as pd
import io

app = Flask(__name__)

# Created By → Counter mapping
created_by_counter_map = {
    "Heena Cashier 1": "TC-1",
    "Heena Cashier 2": "TC-2",
    "Heena Cashier 3": "TC-3",
    "Heena Cashier 5": "TC-5",
    "Trampoline Cafe Cashier 1": "Trampoline Cafe",
    "Softy Cone Cashie 2": "Softy Cone",
    "Tea Stall Cashier 1": "Tea Stall",
    "DHABA LAKE INVERTORY": "Dhinchak by the Lake",
    "Snow Canon Cashier 1": "Snow Cashier"
}

# Category definitions
fnb_counters = [
    "MOMO Kiosk", "Softy Corner", "EOD Maggi", "Dhinchak Dhaba",
    "Ice Cream Parlour & Kart", "Dhinchak by the Lake", "Dhinchak Nukkad",
    "Snow Pops n More", "Buffet & Events", "Trampoline Cafe", "Tea Stall"
]
game_counters = [
    "Jump N Fun", "P&H", "Boating", "VR Games", "E-O-D Gun Shooting",
    "Carnival Event", "Carnival Games"
]
annual_pass_items = [
    "Annual Pass", "Annual Pass (Kids)", "Annual Pass Entry",
    "Annual Pass One Time", "Kids Annual Pass", "Kids Annual Pass One Time",
    "Annual pass Full on masti with S/play"
]
fnb_items = [
    "Just Milk", "Veg Sandwiches", "Veg Pizza", "Veg Pasta",
    "Masala Chai", "Hot Coffee", "Lunch Coupon", "Buffet",
    "Water Bottle", "Coke", "Sprite", "Fanta", "Tea"
]

def resolve_counter_name(row):
    created_by = row.get("Created By", "")
    branch_name = row.get("Branch Name", "")
    return created_by_counter_map.get(created_by, branch_name)

def classify_pos_item(row):
    try:
        item = str(row.get("Item Name", "")).strip()
        branch = str(row.get("Branch Name", "")).strip()
        counter = resolve_counter_name(row)

        if any(ap in item for ap in annual_pass_items):
            return "Annual Pass Revenue"
        if any(item.strip().lower() == f.strip().lower() for f in fnb_items):
        if counter in fnb_counters:
            return "F&B Revenue"
        if counter in game_counters:
            return "Park Games Revenue"
        if branch == "EOD":
            return "Gate Revenue (MV)"
        if branch == "Every Other Day at DME":
            return "Gate Revenue (DME)"
        return "Unclassified"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return "CFO Webhook API is running."

@app.route('/process-cfo', methods=['POST'])
def process_cfo():
    try:
        pos_file = request.files['pos_file']
        upi_file = request.files['upi_file']
        screenshot_file = request.files['screenshot_file']
        event_dsr_file = request.files['event_dsr_file']

        pos_df = pd.read_csv(io.StringIO(pos_file.read().decode('utf-8')))
        upi_df = pd.read_csv(io.StringIO(upi_file.read().decode('utf-8')))
        event_dsr_df = pd.read_excel(event_dsr_file)

        # Classification
        pos_df['Category'] = pos_df.apply(classify_pos_item, axis=1)
        pos_df['Total Amount'] = pos_df['Net Amount'] + pos_df['Taxes']

        revenue_summary = pos_df.groupby('Category')['Total Amount'].sum().round(2).to_dict()
print(revenue_summary)

        return jsonify({
            "status": "success",
            "summary": {
                "POS Rows": len(pos_df),
                "UPI Transactions": len(upi_df),
                "Event Rows": len(event_dsr_df),
                "Screenshot Filename": screenshot_file.filename,
                "Revenue Breakdown": revenue_summary
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
