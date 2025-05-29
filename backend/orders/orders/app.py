from fastapi import FastAPI 

app = FastAPI(dedug=True)
    
from orders.api import api
