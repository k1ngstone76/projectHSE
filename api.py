import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Загрузка данных из CSV
df = pd.read_csv("Road Accident Data.csv")
accidents_db = df.to_dict(orient="records")


# Модель для валидации входных данных
class Accident(BaseModel):
    Accident_Index: Optional[str] = None  # Поле необязательное
    date: str
    location: str
    severity: str


# GET метод для получения данных
@app.get("/accidents", response_model=List[dict])
def get_accidents(
    severity: Optional[str] = Query(None, description="Filter by Accident_Severity"),
    day_of_week: Optional[str] = Query(None, description="Filter by Day_of_Week"),
    limit: int = Query(10, description="Limit the number of results"),
):
    filtered_accidents = accidents_db

    # Фильтрация по `Accident_Severity`
    if severity:
        filtered_accidents = [acc for acc in filtered_accidents if acc.get("Accident_Severity") == severity]

    # Фильтрация по `Day_of_Week`
    if day_of_week:
        filtered_accidents = [acc for acc in filtered_accidents if acc.get("Day_of_Week") == day_of_week]

    # Применение лимита
    return filtered_accidents[:limit]


# POST метод для добавления новых данных
@app.post("/accidents", response_model=dict)
def add_or_update_accident(accident: Accident):
    global accidents_db

    # Проверка уникальности `Accident_Index`, если он указан
    if accident.Accident_Index:
        for record in accidents_db:
            if record.get("Accident_Index") == accident.Accident_Index:
                raise HTTPException(
                    status_code=400,
                    detail=f"Accident with index {accident.Accident_Index} already exists.",
                )

    # Добавление новой записи
    new_accident = {
        "Accident_Index": accident.Accident_Index if accident.Accident_Index else f"NEW_{len(accidents_db) + 1}",
        "Accident Date": accident.date,
        "Local_Authority_(District)": accident.location,
        "Accident_Severity": accident.severity,
    }
    accidents_db.append(new_accident)

    # Сохранение изменений в CSV
    updated_df = pd.DataFrame(accidents_db)
    updated_df.to_csv("Road Accident Data.csv", index=False)

    return new_accident


# Условие запуска Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
