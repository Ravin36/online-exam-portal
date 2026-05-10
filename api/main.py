from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

app = FastAPI(title="Online Examination Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "API is running without a database backend"}


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def database_removed(path: str):
    return JSONResponse(
        status_code=501,
        content={
            "detail": "Database-backed API routes have been removed.",
            "path": f"/api/{path}",
        },
    )


handler = Mangum(app)
