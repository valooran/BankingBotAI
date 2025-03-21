from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, account_routes

app = FastAPI()

# CORS – allows Angular to call backend from a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router)
app.include_router(account_routes.router)

@app.get("/")
def read_root():
    return {"message": "Backend API is running"}