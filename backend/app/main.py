from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, account_routes, chat_routes

app = FastAPI()

origins = [
    "http://localhost:4200", 
    "https://banking-bot-ai.vercel.app"
]
# CORS – allows Angular to call backend from a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router)
app.include_router(account_routes.router)
app.include_router(chat_routes.router)

@app.get("/")
def read_root():
    return {"message": "Backend API is running"}