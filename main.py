from fastapi import FastAPI, Request, HTTPException, Query
import pandas as pd
import os
import gspread
from typing import Optional
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI(
    title="Inventory API",
    version="1.2",
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
    stock: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    trim: Optional[str] = None,
    drivetrain: Optional[str] = None,
    year: Optional[int] = None,
    price: Optional[float] = None,
    mileage: Optional[float] = None,
    condition: Optional[str] = None,
    color: Optional[str] = None,
    interior_color: Optional[str] = None,
    segment: Optional[str] = None,
    body_type: Optional[str] = None,
    vin: Optional[str] = None,
    dealer: Optional[str] = None,
    description: Optional[str] = None,
    packages: Optional[str] = None,
    equipment: Optional[str] = None,
    highlights: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = Query(50, description="Max number of results to return"),
    offset: int = Query(0, description="Starting index for pagination")
):
    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    filtered_df = df.copy()

    def contains(field, val):
        return filtered_df[field].str.contains(val, case=False, na=False)

    if stock:
        filtered_df = filtered_df[filtered_df["Stock"].str.lower() == stock.lower()]
    if vin:
        filtered_df = filtered_df[filtered_df["VIN"].str.lower() == vin.lower()]
    if make:
        filtered_df = filtered_df[contains("Make", make)]
    if model:
        filtered_df = filtered_df[contains("Model", model)]
    if trim:
        filtered_df = filtered_df[contains("Trim", trim)]
    if drivetrain:
        filtered_df = filtered_df[contains("Drivetrain", drivetrain)]
    if condition:
        filtered_df = filtered_df[contains("Condition", condition)]
    if color:
        filtered_df = filtered_df[contains("Exterior Specific Color", color)]
    if interior_color:
        filtered_df = filtered_df[contains("Interior Specific Color", interior_color)]
    if segment:
        filtered_df = filtered_df[contains("Segment", segment)]
    if body_type:
        filtered_df = filtered_df[contains("Body Type", body_type)]
    if dealer:
        filtered_df = filtered_df[contains("Dealer Name", dealer)]
    if description:
        filtered_df = filtered_df[contains("Description", description)]
    if packages:
        filtered_df = filtered_df[contains("Packages", packages)]
    if equipment:
        filtered_df = filtered_df[contains("Popular Equipment", equipment)]
    if highlights:
        filtered_df = filtered_df[contains("Highlights", highlights)]
    if year:
        filtered_df = filtered_df[filtered_df["Year"].astype(int) == year]
    if price:
        filtered_df = filtered_df[filtered_df["Price"].astype(float) <= price]
    if mileage:
        filtered_df = filtered_df[filtered_df["Mileage"].astype(float) <= mileage]

    if keyword:
        kw = keyword.lower()
        fuzzy_mask = pd.Series(False, index=filtered_df.index)
        for col in ["Make", "Model", "Trim", "Drivetrain", "Condition", "Exterior Specific Color",
                    "Interior Specific Color", "Segment", "Body Type", "Dealer Name", "Description",
                    "Packages", "Popular Equipment", "Highlights"]:
            fuzzy_mask |= filtered_df[col].astype(str).str.lower().str.contains(kw, na=False)
        filtered_df = filtered_df[fuzzy_mask]

    result = filtered_df.iloc[offset:offset + limit]
    return result.to_dict(orient="records")
