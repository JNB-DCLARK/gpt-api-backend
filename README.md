# GPT Inventory API (Google Sheets)

This backend provides a `/search` endpoint for use with a Custom GPT to query live dealership inventory from a Google Sheet.

## 🔧 Setup Instructions (GitHub)

1. Clone or unzip this repo.
2. Create a new GitHub repo (e.g., `gpt-api-backend`).
3. In terminal:

```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/gpt-api-backend.git
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

4. On [https://render.com](https://render.com):
   - Create a Web Service from this repo
   - Add **Secret File**: Upload your Google service account JSON as `/etc/secrets/ai-car-cloud.json`
   - Add **Environment Variable**: `GPT_API_KEY=your-secret-key`
   - Use `uvicorn main:app --host 0.0.0.0 --port 10000` as the start command

5. Upload `openapi.json` to your Custom GPT under the Actions tab and set `Authorization: Bearer your-secret-key`.

You're now live. ✅
