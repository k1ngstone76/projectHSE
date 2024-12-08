import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

df = pd.read_csv("Road Accident Data.csv")
accidents_db = df.to_dict(orient="records")

# Model for validating input data
class Accident(BaseModel):
    Accident_Index: Optional[str] = None  
    date: str
    location: str
    severity: str
    weather: str
    casualties: int
# GET method to get data
@app.get("/accidents", response_model=List[dict])
def get_accidents(
    severity: Optional[str] = Query(None, description="Filter by Accident_Severity"),
    day_of_week: Optional[str] = Query(None, description="Filter by Day_of_Week"),
    limit: int = Query(10, description="Limit the number of results"),
):
    filtered_accidents = accidents_db

    # Filter by `Accident_Severity`
    if severity:
        filtered_accidents = [acc for acc in filtered_accidents if acc.get("Accident_Severity") == severity]

    # Filter by `Day_of_Week`
    if day_of_week:
        filtered_accidents = [acc for acc in filtered_accidents if acc.get("Day_of_Week") == day_of_week]

    # Applying a limit
    return [
        {
            "Accident Date": acc.get("Accident Date"),
            "Local Authority": acc.get("Local_Authority_(District)"),
            "Severity": acc.get("Accident_Severity"),
            "Day of Week": acc.get("Day_of_Week"),
        }
        for acc in filtered_accidents[:limit]
    ]



@app.post("/accidents", response_model=dict)
def add_or_update_accident(accident: Accident):
    global accidents_db

    # Check required fields
    required_fields = ['date', 'location', 'severity', 'casualties']
    
    for field in required_fields:
        if not getattr(accident, field):
            raise HTTPException(status_code=400, detail=f"{field} is required.")
    
    # Проверка уникальности `Accident_Index`, если он указан
    if accident.Accident_Index:
        for record in accidents_db:
            if record.get("Accident_Index") == accident.Accident_Index:
                raise HTTPException(
                    status_code=400,
                    detail=f"Accident with index {accident.Accident_Index} already exists.",
                )

    # Create a new entry
    new_accident = {
        "Accident_Index": accident.Accident_Index if accident.Accident_Index else f"{len(accidents_db) + 1}",
        "Accident Date": accident.date,
        "Local_Authority_(District)": accident.location,
        "Accident_Severity": accident.severity,
        "Weather_Conditions": accident.weather,  
        "Number_of_Casualties": accident.casualties  
    }

    # Fill missing columns with 'unknown' value
    all_columns = df.columns 
    new_accident = {col: new_accident.get(col, "unknown") for col in all_columns}

    accidents_db.append(new_accident)

    # Save changes to CSV
    updated_df = pd.DataFrame(accidents_db)
    updated_df.to_csv("Road Accident Data.csv", index=False)

    return new_accident





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
