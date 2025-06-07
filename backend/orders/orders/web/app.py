from fastapi import FastAPI 

app = FastAPI(dedug=True)
    
from orders.web.api import api