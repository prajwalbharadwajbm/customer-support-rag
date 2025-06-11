from contextlib import asynccontextmanager
from functools import lru_cache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from internal.env_utils import SettingEnv
from routes.chat import router as chat_router
from dependencies import initialize_chain, clear_chain
from utils.logging import setup_logging

# Initialize logging configuration
setup_logging()

@asynccontextmanager    
async def lifespan(app: FastAPI):
    # Initialize the chain when the app starts
    initialize_chain()
    yield
    # Clear the chain when the app shuts down
    clear_chain()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache
def get_settings():
    return SettingEnv()

app.include_router(chat_router)
