import os
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'

from services import chat_services
from langchain_core.runnables import Runnable

chain= None

def initialize_chain():
    global chain
    chain = chat_services.chat_chain()

def clear_chain():
    global chain
    chain = None

def get_chain() -> Runnable:
    if chain is None:
        raise RuntimeError("Chain not initialized")
    return chain
