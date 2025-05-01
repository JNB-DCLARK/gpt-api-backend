from fastapi import FastAPI, Request, HTTPException
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Correct placement of app initialization
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

@app.get("/search")

def search_inventory(request: Request):
    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    print("🔥 RETURNING rows:", len(df))
    print("🔍 First row:", df.iloc[0].to_dict() if not df.empty else "EMPTY")
    return df.head(5).to_dict(orient="records")

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
