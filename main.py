from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from pydantic import BaseModel, HttpUrl
from typing import List
from datetime import datetime
import pytz

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_FILE = "urls.db"

class URLModel(BaseModel):
    url: HttpUrl

class URLRecord(BaseModel):
    id: int
    url: str
    created_at: str

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_urls() -> List[URLRecord]:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, url, created_at FROM urls ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [URLRecord(id=row[0], url=row[1], created_at=row[2]) for row in rows]

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    urls = get_all_urls()
    return templates.TemplateResponse("index.html", {"request": request, "urls": urls})

@app.post("/add-url")
async def add_url(url: URLModel):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        local_tz = pytz.timezone('Europe/Berlin')
        now = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cursor.execute('INSERT INTO urls (url, created_at) VALUES (?, ?)', (str(url.url), now))
        conn.commit()
        conn.close()
        return {"message": "URL added successfully", "url": str(url.url)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding URL: {str(e)}")

@app.post("/add-url-form")
async def add_url_form(request: Request, url: str = Form(...)):
    try:
        URLModel(url=url)  # Validate URL
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        local_tz = pytz.timezone('Europe/Berlin')
        now = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cursor.execute('INSERT INTO urls (url, created_at) VALUES (?, ?)', (url, now))
        conn.commit()
        conn.close()
        urls = get_all_urls()
        return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "success": "URL added successfully!"})
    except Exception as e:
        urls = get_all_urls()
        return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "error": f"Error adding URL: {str(e)}"})

@app.post("/delete-url")
async def delete_url(url_id: int = Form(...)):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM urls WHERE id = ?', (url_id,))
        conn.commit()
        conn.close()
        return {"message": "URL deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting URL: {str(e)}")

@app.post("/delete-url-form")
async def delete_url_form(request: Request, url_id: int = Form(...)):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM urls WHERE id = ?', (url_id,))
        conn.commit()
        conn.close()
        urls = get_all_urls()
        return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "success": "URL deleted successfully!"})
    except Exception as e:
        urls = get_all_urls()
        return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "error": f"Error deleting URL: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
