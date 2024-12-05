from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Загрузка данных
data = pd.read_csv("Road Accident Data.csv")

# Модель данных для POST запроса
class Accident(BaseModel):
    Date: str
    Location: str
    Accident_Severity: str
    Number_of_Vehicles: int
    Number_of_Casualties: int

# GET метод с фильтрацией по параметрам
@app.get("/accidents/")
async def get_accidents(severity: str = Query(None), limit: int = 10, offset: int = 0):
    filtered_data = data
    if severity:
        filtered_data = data[data['Accident_Severity'] == severity]
    return filtered_data.iloc[offset: offset + limit].to_dict(orient="records")

# POST метод для добавления новой записи
@app.post("/accidents/")
async def create_accident(accident: Accident):
    global data
    new_data = pd.DataFrame([accident.dict()])
    data = pd.concat([data, new_data], ignore_index=True)
    return {"message": "New accident added", "data": accident.dict()}
