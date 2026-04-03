from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import auth, extract

app = FastAPI(
    title="Marksheet Extractor API",
    description="""
    An AI-powered API that extracts structured data from marksheets (images or PDFs).
    
    ## How to Use
    1. Call **/auth/token** with username and password to get a JWT token
    2. Click **Authorize** button and paste the token
    3. Call **/marksheet/extract** with your marksheet file
    
    ## Default Credentials
    - Username: **admin**
    - Password: **admin123**
    """,
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(extract.router, prefix="/marksheet", tags=["Extraction"])

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("app/static/index.html")