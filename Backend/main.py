from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .simulations.model import run_simulation
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Config(BaseModel):
    total_population: int
    num_time_steps: int
    inheritance_tax_rate: float
    wealth_tax: float
    cg_tax: float
    wealth_per_decile: list[float]
    birth_rate: list[float]
    death_rate: list[float]
    net_migration: list[float]
    rate_of_return: list[float]
    savings_rate: list[float]
    wage_band_low: list[float]
    wage_band_high: list[float]
    unemployment_rate: list[float]

@app.post("/simulate")
def simulate(config: Config):
    results = run_simulation(config.dict())
    return results
    
@app.get("/")
def read_root():
    return {"message": "Backend is running"}
