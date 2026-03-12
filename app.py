from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# ===== Google Sheets =====
SHEET_ID = "1PdxU5I4H1sOLK47_HrS_72Tpxxlqmt75xVPJp_xNa6M"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

def load_data():
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

@app.route("/")
def index():
    govs = sorted(df["المحافظة"].dropna().unique().tolist())
    cities = sorted(df["المنطقة / المدينة"].dropna().unique().tolist())
    types = sorted(df["نوع مقدم الخدمة"].dropna().unique().tolist())
    specialties = sorted(df["التخصص"].dropna().unique().tolist())

    return render_template("index.html",
        govs=govs,
        cities=cities,
        types=types,
        specialties=specialties
    )

@app.route("/search")
def search():
    filtered = df.copy()

    gov = request.args.get("gov", "الكل")
    city = request.args.get("city", "الكل")
    type_ = request.args.get("type", "الكل")
    specialty = request.args.get("specialty", "الكل")
    name = request.args.get("name", "").strip()

    if gov != "الكل":
        filtered = filtered[filtered["المحافظة"] == gov]
    if city != "الكل":
        filtered = filtered[filtered["المنطقة / المدينة"] == city]
    if type_ != "الكل":
        filtered = filtered[filtered["نوع مقدم الخدمة"] == type_]
    if specialty != "الكل":
        filtered = filtered[filtered["التخصص"] == specialty]
    if name:
        filtered = filtered[
            filtered["مقدم الخدمة"]
            .astype(str)
            .str.contains(name, case=False, na=False)
        ]

    result = filtered.fillna("").to_dict(orient="records")
    columns = list(filtered.columns)

    return jsonify({
        "data": result,
        "columns": columns,
        "count": len(result)
    })

@app.route("/refresh")
def refresh():
    global df
    df = load_data()
    return jsonify({"status": "✅ البيانات اتحدثت!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
