# # -*- coding: utf-8 -*-
# from flask import Flask, render_template, request, jsonify, send_from_directory
# import pandas as pd, os, datetime, json

# BASE = os.path.dirname(__file__)
# DATA_CSV = os.path.join(BASE, "ev_sales_india.csv")

# app = Flask(__name__, static_folder="static", template_folder="templates")
# app.config["JSON_SORT_KEYS"] = False

# def load_df():
#     try:
#         df = pd.read_csv(DATA_CSV, dtype=str, encoding='utf-8').fillna("")
#     except UnicodeDecodeError:
#         df = pd.read_csv(DATA_CSV, dtype=str, encoding='utf-16').fillna("")
#     return df


# @app.route("/")
# def home():
#     return render_template("home.html")

# @app.route("/dashboard")
# def dashboard():
#     df = load_df()
#     total = int(df['EV_Sales_Quantity'].sum()) if not df.empty else 0
#     top_state = df.groupby('State')['EV_Sales_Quantity'].sum().sort_values(ascending=False).head(1)
#     top_state = top_state.index[0] if not top_state.empty else "N/A"
#     top_type = df.groupby('Vehicle_Type')['EV_Sales_Quantity'].sum().sort_values(ascending=False).head(1)
#     top_type = top_type.index[0] if not top_type.empty else "N/A"
#     years = sorted(df['Year'].dropna().unique().tolist(), key=lambda x: int(x)) if 'Year' in df.columns else []
#     states = sorted(df['State'].dropna().unique().tolist())
#     return render_template("dashboard.html", total=total, top_state=top_state, top_type=top_type, years=years, states=states)

# @app.route("/analytics")
# def analytics():
#     df = load_df()
#     years = sorted(df['Year'].dropna().unique().tolist(), key=lambda x: int(x)) if 'Year' in df.columns else []
#     states = sorted(df['State'].dropna().unique().tolist())
#     vehicle_types = sorted(df['Vehicle_Type'].dropna().unique().tolist())
#     return render_template("analytics.html", years=years, states=states, vehicle_types=vehicle_types)

# @app.route("/reports")
# def reports():
#     return render_template("reports.html")
# @app.route('/forecast')
# def forecast():
#     return render_template("forecast.html")


# # API: summary for dashboard charts
# @app.route("/api/summary")
# def api_summary():
#     df = load_df()
#     if df.empty:
#         return jsonify({"by_year":[], "by_state":[], "by_type":[]})
#     by_year = df.groupby('Year', as_index=False)['EV_Sales_Quantity'].sum().sort_values('Year').to_dict(orient='records')
#     by_state = df.groupby('State', as_index=False)['EV_Sales_Quantity'].sum().sort_values('EV_Sales_Quantity', ascending=False).head(12).to_dict(orient='records')
#     by_type = df.groupby('Vehicle_Type', as_index=False)['EV_Sales_Quantity'].sum().sort_values('EV_Sales_Quantity', ascending=False).to_dict(orient='records')
#     return jsonify({"by_year":by_year, "by_state":by_state, "by_type":by_type})

# # API: filtered data for analytics (POST JSON)
# @app.route("/api/filter", methods=["POST"])
# def api_filter():
#     payload = request.get_json() or {}
#     year = str(payload.get("year","")).strip()
#     state = payload.get("state","").strip()
#     vtype = payload.get("vehicle_type","").strip()
#     df = load_df()
#     if df.empty:
#         return jsonify({"kpi": {"total_units":0,"rows":0}, "table":[]})
#     if year:
#         df = df[df['Year'].astype(str)==str(year)]
#     if state:
#         df = df[df['State']==state]
#     if vtype:
#         df = df[df['Vehicle_Type']==vtype]
#     kpi = {"total_units": int(df['EV_Sales_Quantity'].sum()), "rows": len(df)}
#     table = df.head(500).to_dict(orient='records')
#     return jsonify({"kpi":kpi, "table":table})

# # Forecast (mock predictor) POST => returns year + prediction
# @app.route("/api/forecast", methods=["POST"])
# def api_forecast():
#     body = request.get_json() or {}
#     target_year = int(body.get("year", datetime.datetime.utcnow().year + 1))
#     df = load_df()
#     base = int(df['EV_Sales_Quantity'].sum()) if not df.empty else 1000
#     last_year = int(df['Year'].max()) if ('Year' in df and not df.empty) else datetime.datetime.utcnow().year
#     years_ahead = max(0, target_year - last_year)
#     # naive modeled growth: 25% per year on total (demo)
#     prediction = int(base * ((1 + 0.25) ** years_ahead))
#     return jsonify({"year": target_year, "prediction": prediction, "base_total": base})

# # static file helper (not required, but safe)
# @app.route("/static/<path:filename>")
# def static_files(filename):
#     return send_from_directory(os.path.join(BASE,"static"), filename)

# if __name__ == "__main__":
#     print("Starting EV Insight Poseify (http://127.0.0.1:5000)")
#     app.run(debug=True, port=5000)
from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

# ----------------------------
# Configuration
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CSV = os.path.join(BASE_DIR, "ev_sales_india.csv")


# ----------------------------
# Data Loader
# ----------------------------
def load_df():
    """Load and clean EV dataset safely."""
    print(f"📁 Attempting to load data from: {DATA_CSV}")

    if not os.path.exists(DATA_CSV):
        print(f"❌ CSV not found at: {DATA_CSV}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATA_CSV, encoding='utf-8')
        print(f"✅ Loaded file successfully: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"⚠️ Error reading CSV: {e}")
        return pd.DataFrame()

    # --- Clean column names ---
    df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]
    df.fillna("", inplace=True)
    print("🧹 Cleaned columns:", df.columns.tolist())

    # --- Fix numeric column ---
    if "EV_Sales_Quantity" in df.columns:
        df["EV_Sales_Quantity"] = pd.to_numeric(df["EV_Sales_Quantity"], errors="coerce").fillna(0)

    # --- Ensure 'Year' column exists ---
    if "Year" not in df.columns:
        print("⚠️ 'Year' column missing — deriving from Date...")
        if "Date" in df.columns:
            df["Year"] = pd.to_datetime(df["Date"], errors="coerce").dt.year
        else:
            df["Year"] = pd.NaT

    # --- Ensure 'Month_Name' column exists ---
    if "Month_Name" not in df.columns:
        if "Month" in df.columns:
            # Handle both numeric or text months
            try:
                df["Month_Name"] = pd.to_datetime(df["Month"].astype(str), format='%b', errors='coerce').dt.month_name()
            except:
                df["Month_Name"] = pd.to_datetime(df["Month"], errors='coerce').dt.month_name()
        elif "Date" in df.columns:
            df["Month_Name"] = pd.to_datetime(df["Date"], errors="coerce").dt.month_name()
        else:
            df["Month_Name"] = ""

    # --- Final sanity ---
    df.dropna(subset=["Year"], inplace=True)
    df["Year"] = df["Year"].astype(int)
    print("📊 Final DataFrame Columns:", df.columns.tolist())

    return df



# ----------------------------
# Routes
# ----------------------------
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/analytics')
def analytics():
    return render_template("analytics.html")



@app.route('/reports')
def reports():
    df = load_df()
    years = sorted(df['Year'].dropna().unique().tolist())
    states = sorted(df['State'].dropna().unique().tolist())
    return render_template("reports.html", years=years, states=states)



# ----------------------------
# API Summary Endpoint
# ----------------------------
@app.route('/api/summary')
def api_summary():
    df = load_df()

    # ---- Yearly summary ----
    by_year = (
        df.groupby("Year", as_index=False)["EV_Sales_Quantity"]
        .sum()
        .sort_values("Year")
        .to_dict(orient="records")
    )

    # ---- State summary ----
    if "State" in df.columns:
        by_state = (
            df.groupby("State", as_index=False)["EV_Sales_Quantity"]
            .sum()
            .sort_values("EV_Sales_Quantity", ascending=False)
            .to_dict(orient="records")
        )
    else:
        by_state = []

    # ---- Type summary ----
    if "Vehicle_Type" in df.columns:
        by_type = (
            df.groupby("Vehicle_Type", as_index=False)["EV_Sales_Quantity"]
            .sum()
            .sort_values("EV_Sales_Quantity", ascending=False)
            .to_dict(orient="records")
        )
    else:
        by_type = []

    # ---- Month summary ----
    if "Month_Name" in df.columns:
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        df["Month_Name"] = pd.Categorical(df["Month_Name"], categories=month_order, ordered=True)
        by_month = (
           df.groupby("Month_Name", as_index=False, observed=True)["EV_Sales_Quantity"]
            .sum()
            .sort_values("Month_Name")
            .to_dict(orient="records")
        )
    else:
        by_month = []

    # ---- Category summary ----
    if "Vehicle_Category" in df.columns:
        by_category = (
            df.groupby(["Vehicle_Category", "Vehicle_Class"], as_index=False)["EV_Sales_Quantity"]
            .sum()
            .sort_values("EV_Sales_Quantity", ascending=False)
            .to_dict(orient="records")
        )
    else:
        by_category = []

    # ---- KPI Metrics (NEW for Dashboard Top Chips) ----
    total_units = int(df["EV_Sales_Quantity"].sum()) if "EV_Sales_Quantity" in df.columns else 0
    top_state = (
        df.groupby("State")["EV_Sales_Quantity"].sum().idxmax()
        if "State" in df.columns and not df.empty
        else "N/A"
    )

    return jsonify({
        "by_year": by_year,
        "by_state": by_state,
        "by_type": by_type,
        "by_month": by_month,
        "by_category": by_category,
        "total_units": total_units,
        "top_state": top_state
    })
from flask import request, jsonify

@app.route('/api/filter', methods=['POST'])
def api_filter():
    df = load_df()
    filters = request.get_json() or {}

    year = filters.get('year')
    state = filters.get('state')
    vehicle_type = filters.get('vehicle_type')

    # Apply filters dynamically
    if year:
        df = df[df['Year'].astype(str) == str(year)]
    if state:
        df = df[df['State'].str.lower() == state.lower()]
    if vehicle_type:
        df = df[df['Vehicle_Type'].str.lower() == vehicle_type.lower()]

    # KPIs
    total_units = int(df['EV_Sales_Quantity'].sum()) if not df.empty else 0
    rows = len(df)
    top_state = df['State'].value_counts().idxmax() if not df.empty else '-'
    top_type = df['Vehicle_Type'].value_counts().idxmax() if not df.empty else '-'

    # Chart data
    by_state = (
        df.groupby("State", as_index=False)["EV_Sales_Quantity"]
        .sum().sort_values("EV_Sales_Quantity", ascending=False).to_dict(orient="records")
    )

    by_type = (
        df.groupby("Vehicle_Type", as_index=False)["EV_Sales_Quantity"]
        .sum().sort_values("EV_Sales_Quantity", ascending=False).to_dict(orient="records")
    )

    by_manufacturer = (
        df.groupby("Manufacturer", as_index=False)["EV_Sales_Quantity"]
        .sum().sort_values("EV_Sales_Quantity", ascending=False).to_dict(orient="records")
    )

    # Keep month order for trend chart
    month_order = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    df["Month_Name"] = pd.Categorical(df["Month_Name"], categories=month_order, ordered=True)
    by_month = (
        df.groupby("Month_Name", as_index=False)["EV_Sales_Quantity"]
        .sum().sort_values("Month_Name").to_dict(orient="records")
    )

    return jsonify({
        "kpi": {
            "total_units": total_units,
            "rows": rows,
            "top_state": top_state,
            "top_type": top_type
        },
        "charts": {
            "by_state": by_state,
            "by_type": by_type,
            "by_manufacturer": by_manufacturer,
            "by_month": by_month
        }
    })



@app.route('/api/options')
def api_options():
    df = load_df()

    years = sorted(df['Year'].dropna().unique().tolist())
    states = sorted(df['State'].dropna().unique().tolist())
    vehicle_types = sorted(df['Vehicle_Type'].dropna().unique().tolist())

    return jsonify({
        "years": years,
        "states": states,
        "vehicle_types": vehicle_types
    })

from flask import send_file, request
import io

@app.route('/api/report', methods=['POST'])
def api_report():
    df = load_df()
    params = request.get_json()
    year = params.get('year')
    state = params.get('state')

    # Apply filters
    if year:
        df = df[df['Year'] == int(year)]
    if state:
        df = df[df['State'] == state]

    total_units = int(df['EV_Sales_Quantity'].sum())
    top_state = df.groupby('State')['EV_Sales_Quantity'].sum().idxmax() if not df.empty else '-'
    top_manufacturer = df.groupby('Manufacturer')['EV_Sales_Quantity'].sum().idxmax() if not df.empty else '-'

    table_data = df.groupby(['Year','State','Manufacturer','Vehicle_Type'], as_index=False)['EV_Sales_Quantity'].sum().to_dict(orient='records')

    return jsonify({
        "kpi": {
            "total_units": total_units,
            "top_state": top_state,
            "top_manufacturer": top_manufacturer,
            "rows": len(table_data)
        },
        "table": table_data
    })


@app.route('/download_report')
def download_report():
    fmt = request.args.get('format', 'csv')
    year = request.args.get('year')
    state = request.args.get('state')

    df = load_df()
    if year:
        df = df[df['Year'] == int(year)]
    if state:
        df = df[df['State'] == state]

    filename = f"ev_report_{year or 'all'}_{state or 'india'}"

    buf = io.BytesIO()
    if fmt == 'xlsx':
        df.to_excel(buf, index=False)
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"{filename}.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif fmt == 'pdf':
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"{filename}.pdf", mimetype="application/pdf")
    else:
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"{filename}.csv", mimetype="text/csv")


# ----------------------------
# Run
# ----------------------------
if __name__ == '__main__':
    print("🚀 Starting EV Insight (Enhanced Dashboard Mode)")
    app.run(debug=True)
