import os
import joblib
import pandas as pd
import numpy as np
from typing import List, AsyncIterator, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import AliasChoices, BaseModel, Field, ConfigDict
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional


from app.database import init_db, sessionLocal, Assesment_Record, get_db

# Define correct paths using raw strings
Model_path = r"C:\Users\lenovo\OneDrive\Desktop\Health_Care_CRM\MLOPS\models\healthcare_model.pkl"
preprocessor_path = r"C:\Users\lenovo\OneDrive\Desktop\Health_Care_CRM\MLOPS\models\preprocessor.pkl"

model = None
preprocessor = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global model, preprocessor
    try:
        init_db()
        print("SQLite Database initialized successfully!")
        model = joblib.load(Model_path)
        preprocessor = joblib.load(preprocessor_path)
        print("Model and Preprocessor loaded successfully into FastAPI!")
    except Exception as e:
        print(f"Error during startup initialization: {e}")
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
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatientRecord(BaseModel):
    Patient_name: Optional[str] = Field(
        default="Unknown", 
        validation_alias=AliasChoices("Patient Name", "patient_name", "Name"),
        serialization_alias="Patient Name"
    )
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

        drop_cols = ['Patient Name', 'Date of Admission', 'Discharge Date', 'Doctor', 'Hospital', 'Room Number']
        input_data = input_data.drop(columns=drop_cols, errors='ignore')

        processed_data = preprocessor.transform(input_data)
        pred = int(model.predict(processed_data)[0])
        prob = float(model.predict_proba(processed_data)[0][1])

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
def predict_batch_records(records: List[PatientRecord], db: Session = Depends(get_db)):
    if model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Model or Preprocessor not loaded")
    if not records:
        raise HTTPException(status_code=400, detail="At least one patient record is required")
    try:
        df = pd.DataFrame([r.model_dump(by_alias=True) for r in records])
        
        df["Date of Admission"] = pd.to_datetime(df["Date of Admission"], errors='coerce').fillna(pd.Timestamp("2023-01-01"))
        df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], errors='coerce').fillna(pd.Timestamp("2023-01-05"))
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

            record_data = records[i].model_dump(by_alias=True)

            patient_name = (
                record_data.get("Patient Name") 
                or record_data.get("patient_name") 
                or record_data.get("Name") 
                or "Unknown"
            )

            new_record = Assesment_Record(
                Patient_name=patient_name,
                age=record_data.get("Age", 0),
                medical_condition=record_data.get("Medical Condition", "None"),
                billing_amount=record_data.get("Billing Amount", 0.0),
                probability=round(pr, 4),
                risk_status=status_text
            )
            db.add(new_record)

            results.append({
                "row_index": i, 
                "Prediction": p, 
                "Probability": round(pr, 4),
                "status": status_text
            })
            
        db.commit()
        return {"total_processed": len(records), "results": results}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/assessment-history")
def get_assessment_history(db: Session = Depends(get_db)):
    try:
        records = db.query(Assesment_Record).all()
        
        history_list = []
        for r in records:
            history_list.append({
                "id": r.id,
                "Assessment_Timestamp": r.assesment_timestamp,
                "Patient Name": r.Patient_name,
                "Age": r.age,
                "Medical Condition": r.medical_condition,
                "Billing Amount": r.billing_amount,
                "Probability": r.probability,
                "Risk_Status": r.risk_status
            })
            
        return {
            "total_records": len(history_list),
            "history": history_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))