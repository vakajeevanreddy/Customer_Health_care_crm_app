import os
import joblib
import pandas as pd
import numpy as np
from typing import List, AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from fastapi.middleware.cors import CORSMiddleware

# Define paths to artifacts
Model_path = r"C://Users//lenovo//OneDrive//Desktop//Health_Care_CRM//MLOPS//models//healthcare_model.pkl"
preprocessor_path = r"C://Users//lenovo//OneDrive//Desktop//Health_Care_CRM//MLOPS//models//preprocessor.pkl"

model = None
preprocessor = None

# Modern FastAPI Lifespan context manager replacing @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global model, preprocessor
    try:
        model = joblib.load(Model_path)
        preprocessor = joblib.load(preprocessor_path)
        print("Model and Preprocessor loaded successfully into FastAPI!")
    except Exception as e:
        print(f"Error loading artifacts : {e}")
    yield
    # Clean up artifacts on shutdown if needed
    model = None
    preprocessor = None

app = FastAPI(
    title="Health Care CRM Inference API",
    description="API for scoring patient records using the best-performing trained ML model",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatientRecord(BaseModel):
    Age: int = Field(..., examples=[45])
    Gender: str = Field(..., examples=["Male"])
    Blood_Type: str = Field(..., alias="Blood Type", examples=["O+"])
    Medical_Condition: str = Field(..., alias="Medical Condition", examples=["Diabetes"])
    Date_of_Admission: str = Field(..., alias="Date of Admission", examples=["2023-01-15"])
    Doctor: str = Field(..., examples=["Dr. Smith"])
    Hospital: str = Field(..., examples=["City General"])
    Discharge_Date: str = Field(..., alias="Discharge Date", examples=["2023-01-20"])
    Insurance_Provider: str = Field(..., alias="Insurance Provider", examples=["Blue Cross"])
    Billing_Amount: float = Field(..., alias="Billing Amount", examples=[15000.50])
    Room_Number: int = Field(..., alias="Room Number", examples=[204])
    Admission_Type: str = Field(..., alias="Admission Type", examples=["Emergency"])
    Medication: str = Field(..., examples=["Paracetamol"])

    # Fixed Pydantic V2 Warning using ConfigDict instead of class Config
    model_config = ConfigDict(populate_by_name=True)

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    status: str

@app.get("/")
def home():
    return {"Message": "Healthcare CRM ML Inference API is running successfully."}

@app.post("/predict", response_model=PredictionResponse)
def predict_patient_Record(record: PatientRecord):
    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Model or preprocessor not loaded.")
    try:
        input_data = pd.DataFrame([record.model_dump(by_alias=True)])
        input_data["Date of Admission"] = pd.to_datetime(input_data["Date of Admission"])
        input_data["Discharge Date"] = pd.to_datetime(input_data["Discharge Date"])
        input_data["Length_to_Stay"] = (input_data["Discharge Date"] - input_data["Date of Admission"]).dt.days

        # Change 'Name' to 'Patient Name'
        drop_cols = ['Patient Name', 'Date of Admission', 'Discharge Date', 'Doctor', 'Hospital', 'Room Number']
        input_data = input_data.drop(columns=drop_cols, errors='ignore')

        processed_data = preprocessor.transform(input_data)
        pred = int(model.predict(processed_data)[0])
        prob = float(model.predict_proba(processed_data)[0][1])

        # Map to frontend-friendly risk status strings
        if pred == 1 or prob > 0.7:
            status_text = "high-risk"
        elif prob > 0.4:
            status_text = "moderate-risk"
        else:
            status_text = "low-risk"

        return {
            "prediction": pred,
            "probability": round(prob, 4),
            "status": status_text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predict-batch")
def predict_batch_records(records: List[PatientRecord]):
    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Model or Preprocessor not loaded")
    try:
        df = pd.DataFrame([r.model_dump(by_alias=True) for r in records])
        
        df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
        df["Discharge Date"] = pd.to_datetime(df["Discharge Date"])
        df["Length_to_Stay"] = (df["Discharge Date"] - df["Date of Admission"]).dt.days

        drop_cols = ['Name', 'Date of Admission', 'Discharge Date', 'Doctor', 'Hospital', 'Room Number']
        df_cleaned = df.drop(columns=drop_cols, errors='ignore')

        processed_data = preprocessor.transform(df_cleaned)
        preds = model.predict(processed_data)
        probs = model.predict_proba(processed_data)[:, 1]

        results = []
        for i in range(len(records)):
            p = int(preds[i])
            pr = float(probs[i])
            
            if p == 1 or pr > 0.7:
                status_text = "high-risk"
            elif pr > 0.4:
                status_text = "moderate-risk"
            else:
                status_text = "low-risk"

            results.append({
                "row_index": i, 
                "Prediction": p, 
                "Probability": round(pr, 4),
                "status": status_text
            })
        return {"total_processed": len(records), "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))