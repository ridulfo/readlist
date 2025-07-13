from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import csv
import os
from pydantic import BaseModel, HttpUrl
from typing import List
from datetime import datetime
import pytz

app = FastAPI()
templates = Jinja2Templates(directory="templates")

CSV_FILE = "urls.csv"

class URLModel(BaseModel):
    url: HttpUrl

class URLRecord(BaseModel):
    id: int
    url: str
    created_at: str

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'url', 'created_at'])

def get_all_urls() -> List[URLRecord]:
    if not os.path.exists(CSV_FILE):
        return []
    
    urls = []
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            urls.append(URLRecord(
                id=int(row['id']),
                url=row['url'],
                created_at=row['created_at']
            ))
    
    return sorted(urls, key=lambda x: x.id, reverse=True)

def get_next_id() -> int:
    urls = get_all_urls()
    if not urls:
        return 1
    return max(url.id for url in urls) + 1

def add_url_to_csv(url: str, created_at: str) -> int:
    url_id = get_next_id()
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([url_id, url, created_at])
    return url_id

def delete_url_from_csv(url_id: int) -> bool:
    if not os.path.exists(CSV_FILE):
        return False
    
    urls = []
    found = False
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['id']) != url_id:
                urls.append(row)
            else:
                found = True
    
    if found:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'url', 'created_at'])
            for url in urls:
                writer.writerow([url['id'], url['url'], url['created_at']])
    
    return found

@app.on_event("startup")
async def startup_event():
    init_csv()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    urls = get_all_urls()
    return templates.TemplateResponse("index.html", {"request": request, "urls": urls})

@app.post("/add-url")
async def add_url(url: URLModel):
    try:
        local_tz = pytz.timezone('Europe/Berlin')
        now = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        url_id = add_url_to_csv(str(url.url), now)
        return {"message": "URL added successfully", "url": str(url.url), "id": url_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding URL: {str(e)}")

@app.post("/add-url-form")
async def add_url_form(request: Request, url: str = Form(...)):
    try:
        URLModel(url=url)  # Validate URL
        local_tz = pytz.timezone('Europe/Berlin')
        now = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        add_url_to_csv(url, now)
        urls = get_all_urls()
        return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "success": "URL added successfully!"})
    except Exception as e:
        urls = get_all_urls()
        return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "error": f"Error adding URL: {str(e)}"})

@app.post("/delete-url")
async def delete_url(url_id: int = Form(...)):
    try:
        success = delete_url_from_csv(url_id)
        if success:
            return {"message": "URL deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="URL not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting URL: {str(e)}")

@app.post("/delete-url-form")
async def delete_url_form(request: Request, url_id: int = Form(...)):
    try:
        success = delete_url_from_csv(url_id)
        urls = get_all_urls()
        if success:
            return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "success": "URL deleted successfully!"})
        else:
            return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "error": "URL not found"})
    except Exception as e:
        urls = get_all_urls()
        return templates.TemplateResponse("index.html", {"request": request, "urls": urls, "error": f"Error deleting URL: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
