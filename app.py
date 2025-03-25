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
    item = str(row['Item Name']).lower()
    branch = str(row['Branch Name']).lower()
    created_by = str(row['Created By']).lower()

    # Annual Pass
    if any(k in item for k in ['annual pass', 'full on masti']):
        return 'Annual Pass'

    # F&B by Branch Name (outside gate)
    fnb_branches = [
        'momo kiosk', 'softy corner', 'eod maggi', 'dhinchak dhaba',
        'ice cream parlour & kart', 'dhinchak nukkad', 'snow pops n more',
        'buffet & events', 'trampoline cafe', 'tea stall', 'dhinchak by the lake'
    ]
    if branch in fnb_branches:
        return 'F&B Revenue'

    # F&B by Item (even inside TC-1 to TC-5)
    fnb_items = ['veg sandwich', 'veg pizza', 'veg pasta', 'just milk', 'chai', 'coffee']
    if any(k in item for k in fnb_items):
        return 'F&B Revenue'

    # Games Revenue
    game_branches = [
        'jump n fun', 'p&h', 'boating', 'vr games', 'e-o-d gun shooting',
        'carnival games', 'carnival event'
    ]
    if branch in game_branches:
        return 'Games Revenue'

    # DME Gate Revenue
    if 'dme' in branch:
        return 'Gate Revenue (DME)'

    # Locker Charges → Counted in MV revenue, not in footfall
    if 'locker' in item:
        return 'Gate Revenue (MV)'

    # Gate Revenue (MV) default
    if 'eod' in branch and branch != 'every other day at dme':
        return 'Gate Revenue (MV)'

    return 'Unclassified'

# Apply the classification to the POS data
pos_df['Category'] = pos_df.apply(classify_pos_item, axis=1)

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

