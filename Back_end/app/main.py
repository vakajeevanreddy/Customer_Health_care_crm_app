import os
import csv
from datetime import datetime
import joblib
import pandas as pd
import numpy as np
from typing import List, AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
# Define paths to artifacts
Model_path = r"C://Users//lenovo//OneDrive//Desktop//Health_Care_CRM//MLOPS//models//healthcare_model.pkl"
preprocessor_path = r"C://Users//lenovo//OneDrive//Desktop//Health_Care_CRM//MLOPS//models//preprocessor.pkl"

model = None
preprocessor = None

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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatientRecord(BaseModel):
    Age: Optional[int] = Field(default=30, examples=[45])
    Gender: Optional[str] = Field(default="Unknown", examples=["Male"])
    Blood_Type: Optional[str] = Field(default="O+", alias="Blood Type", examples=["O+"])
    Medical_Condition: Optional[str] = Field(default="None", alias="Medical Condition", examples=["Diabetes"])
    Date_of_Admission: Optional[str] = Field(default="2023-01-01", alias="Date of Admission", examples=["2023-01-15"])
    Doctor: Optional[str] = Field(default="Unknown", examples=["Dr. Smith"])
    Hospital: Optional[str] = Field(default="Unknown", examples=["City General"])
    Discharge_Date: Optional[str] = Field(default="2023-01-05", alias="Discharge Date", examples=["2023-01-20"])
    Insurance_Provider: Optional[str] = Field(default="Unknown", alias="Insurance Provider", examples=["Blue Cross"])
    Billing_Amount: Optional[float] = Field(default=0.0, alias="Billing Amount", examples=[15000.50])
    Room_Number: Optional[int] = Field(default=100, alias="Room Number", examples=[204])
    Admission_Type: Optional[str] = Field(default="Routine", alias="Admission Type", examples=["Emergency"])
    Medication: Optional[str] = Field(default="None", examples=["Paracetamol"])

    model_config = ConfigDict(populate_by_name=True)

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    status: str

@app.get("/")
def home():
    return {"message": "Healthcare CRM ML Inference API is running successfully."}

@app.post("/predict", response_model=PredictionResponse)
def predict_patient_Record(record: PatientRecord):
    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Model or preprocessor not loaded.")
    try:
        input_data = pd.DataFrame([record.model_dump(by_alias=True)])
        input_data["Date of Admission"] = pd.to_datetime(input_data["Date of Admission"])
        input_data["Discharge Date"] = pd.to_datetime(input_data["Discharge Date"])
        input_data["Length_to_Stay"] = (input_data["Discharge Date"] - input_data["Date of Admission"]).dt.days

        drop_cols = ['Patient Name', 'Date of Admission', 'Discharge Date', 'Doctor', 'Hospital', 'Room Number']
        input_data = input_data.drop(columns=drop_cols, errors='ignore')

        processed_data = preprocessor.transform(input_data)
        pred = int(model.predict(processed_data)[0])
        prob = float(model.predict_proba(processed_data)[0][1])

        # Base the risk label on probability so it matches the batch endpoint.
        if prob >= 0.40:
            status_text = "high-risk"
            prediction_code = 1
        elif prob >= 0.25:
            status_text = "moderate-risk"
            prediction_code = 1
        else:
            status_text = "low-risk"
            prediction_code = 0

        return {
            "prediction": prediction_code,
            "probability": round(prob, 4),
            "status": status_text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# THIS WAS MISSING: The batch endpoint that fixes the 404 error
@app.post("/predict-batch")
def predict_batch_records(records: List[PatientRecord]):
    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Model or Preprocessor not loaded")
    if not records:
        raise HTTPException(status_code=400, detail="At least one patient record is required")
    try:
        df = pd.DataFrame([r.model_dump(by_alias=True) for r in records])
        
        # Safe datetime parsing filling NaT if blanks exist
        df["Date of Admission"] = pd.to_datetime(df["Date of Admission"], errors='coerce').fillna(pd.Timestamp("2023-01-01"))
        df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], errors='coerce').fillna(pd.Timestamp("2023-01-05"))
        df["Length_to_Stay"] = (df["Discharge Date"] - df["Date of Admission"]).dt.days

        drop_cols = ['Patient Name', 'Date of Admission', 'Discharge Date', 'Doctor', 'Hospital', 'Room Number']
        df_cleaned = df.drop(columns=drop_cols, errors='ignore')

        processed_data = preprocessor.transform(df_cleaned)
        preds = model.predict(processed_data)
        probs = model.predict_proba(processed_data)[:, 1]

        results = []
        for i in range(len(records)):
            p = int(preds[i])
            pr = float(probs[i])
            
            # Use actual probability ranges to distribute the risk properly
            if pr >= 0.50:
                status_text = "high-risk"
                prediction_code = 1
            elif pr >= 0.35:
                status_text = "moderate-risk"
                prediction_code = 1
            else:
                status_text = "low-risk"
                prediction_code = 0


            row_dict = records[i].model_dump(by_alias=True)
            row_dict.update({
                "Prediction_Code": prediction_code,
                "Probability": round(pr, 4),
                "Risk_Status": status_text,
                "Assessment_Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            csv_filename = os.path.join(os.path.dirname(__file__), "patient_assessments.csv")
            file_exists = os.path.exists(csv_filename)
            with open(csv_filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=row_dict.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row_dict)
            history_path = os.path.join(os.path.dirname(__file__), "patient_assessments_history.csv")
            pd.DataFrame([row_dict]).to_csv(
                history_path,
                mode="a",
                header=not os.path.exists(history_path),
                index=False,
            )
            results.append({
                "row_index": i,
                "Prediction": prediction_code,
                "Probability": round(pr, 4),
                "status": status_text
            })
        return {"total_processed": len(records), "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.get("/assessment-history")
def get_assesment_history():
    csv_filename = "C://Users//lenovo//OneDrive//Desktop//Health_Care_CRM//Back_end//app//patient_assessments_history.csv"
    
    if not os.path.exists(csv_filename):
        return {"total_records": 0, "history": []}
    
    try:
        df = pd.read_csv(csv_filename)
        
        # Strip whitespace from all column headers to prevent hidden spacing mismatches
        df.columns = df.columns.str.strip()
        
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient="records")
        
        return {
            "total_records": len(records),
            "history": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))