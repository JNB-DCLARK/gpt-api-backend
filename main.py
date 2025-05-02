from fastapi import FastAPI, Request, HTTPException, Query
import pandas as pd
import os
import gspread
from typing import Optional
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI(
    title="Inventory API",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

API_KEY = os.getenv("GPT_API_KEY", "988ed1c7591b9085458df556b688be10")
GOOGLE_CREDENTIALS_FILE = "/etc/secrets/ai-car-cloud.json"
SHEET_NAME = "Sheet1"

def load_inventory():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    spreadsheet_id = "14IHso5bytCY2InXw9Ba8-BNUFuNIAjuWmJC14Pr7Vmo"
    sheet = client.open_by_key(spreadsheet_id).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

df = load_inventory()
print("✅ Inventory loaded:", len(df), "rows")
print("🧪 Columns:", df.columns.tolist())

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API is live!",
        "endpoints": ["/search", "/docs", "/health"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/search")
def search_inventory(
    request: Request,
    make: Optional[str] = None,
    model: Optional[str] = None,
    price: Optional[float] = None,
    year: Optional[int] = None,
    color: Optional[str] = None,
    drivetrain: Optional[str] = None,
    limit: int = Query(50, description="Max number of results to return"),
    offset: int = Query(0, description="Starting index for pagination")
):
    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    filtered_df = df.copy()

    if make:
        filtered_df = filtered_df[filtered_df["Make"].str.lower() == make.lower()]
    if model:
        filtered_df = filtered_df[filtered_df["Model"].str.lower() == model.lower()]
    if price:
        filtered_df = filtered_df[filtered_df["Price"].astype(float) <= price]
    if year:
        filtered_df = filtered_df[filtered_df["Year"].astype(int) == year]
    if color:
        filtered_df = filtered_df[filtered_df["Exterior Specific Color"].str.lower().str.contains(color.lower(), na=False)]
    if drivetrain:
        filtered_df = filtered_df[filtered_df["Drivetrain"].str.lower().str.contains(drivetrain.lower(), na=False)]

    result = filtered_df.iloc[offset:offset + limit]
    return result.to_dict(orient="records")
