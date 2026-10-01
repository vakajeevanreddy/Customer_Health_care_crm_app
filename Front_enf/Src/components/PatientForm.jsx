import React, { useState } from "react";
import { predictPatient } from "../api/Api";
import './PatientForm.css';

export default function PatientForm() {
    const [formData, setFormData] = useState({
        "Patient Name": "John Doe",
        Age: 45,
        Gender: "Male",
        "Blood Type": "O+",
        "Medical Condition": "Diabetes",
        "Date of Admission": "2023-01-15",
        Doctor: "Dr. Smith",
        Hospital: "City General",
        "Discharge Date": "2023-01-20",
        "Insurance Provider": "Blue Cross",
        "Billing Amount": 15000.50,
        "Room Number": 204,
        "Admission Type": "Emergency",
        Medication: "Paracetamol"
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Predefined lists for dropdowns
    const medicalConditions = ["Diabetes", "Hypertension", "Asthma", "Cancer", "Injury", "Heart Disease", "Other"];
    const admissionTypes = ["Emergency", "Urgent", "Elective"];
    const genders = ["Male", "Female", "Other"];
    const bloodTypes = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'number' ? parseFloat(value) : value
        });
    };

    const handleDateChange = (field, value) => {
        const updatedData = { ...formData, [field]: value };
        
        if (updatedData["Date of Admission"] && updatedData["Discharge Date"]) {
            const admission = new Date(updatedData["Date of Admission"]);
            const discharge = new Date(updatedData["Discharge Date"]);
            const diffTime = discharge - admission;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (diffDays > 0) {
                const dailyRate = 250;
                const calculatedCost = diffDays * dailyRate;
                updatedData["Billing Amount"] = calculatedCost;
            }
        }
        setFormData(updatedData);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const data = await predictPatient(formData);
            setResult(data);
        } catch (err) {
            setError(err.message || err.toString());
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="crm-container">
            <h2>Healthcare CRM - Patient Risk Assessment</h2>
            <form onSubmit={handleSubmit} className="patient-form">
                {Object.keys(formData).map((key) => {
                    // 1. Render Dropdown for "Medical Condition"
                    if (key === "Medical Condition") {
                        return (
                            <div className="form-group" key={key}>
                                <label>
                                    {key}:
                                    <select name={key} value={formData[key]} onChange={handleChange}>
                                        {medicalConditions.map(cond => (
                                            <option key={cond} value={cond}>{cond}</option>
                                        ))}
                                    </select>
                                </label>
                            </div>
                        );
                    }

                    // 2. Render Dropdown for "Admission Type"
                    if (key === "Admission Type") {
                        return (
                            <div className="form-group" key={key}>
                                <label>
                                    {key}:
                                    <select name={key} value={formData[key]} onChange={handleChange}>
                                        {admissionTypes.map(type => (
                                            <option key={type} value={type}>{type}</option>
                                        ))}
                                    </select>
                                </label>
                            </div>
                        );
                    }

                    // 3. Render Dropdown for Gender
                    if (key === "Gender") {
                        return (
                            <div className="form-group" key={key}>
                                <label>
                                    {key}:
                                    <select name={key} value={formData[key]} onChange={handleChange}>
                                        {genders.map(g => (
                                            <option key={g} value={g}>{g}</option>
                                        ))}
                                    </select>
                                </label>
                            </div>
                        );
                    }

                    // 4. Render Dropdown for Blood Type
                    if (key === "Blood Type") {
                        return (
                            <div className="form-group" key={key}>
                                <label>
                                    {key}:
                                    <select name={key} value={formData[key]} onChange={handleChange}>
                                        {bloodTypes.map(bt => (
                                            <option key={bt} value={bt}>{bt}</option>
                                        ))}
                                    </select>
                                </label>
                            </div>
                        );
                    }

                    // 5. Standard inputs for dates, numbers, and text fields
                    return (
                        <div className="form-group" key={key}>
                            <label>
                                {key}:
                                <input
                                    type={
                                        key === "Date of Admission" || key === "Discharge Date"
                                            ? "date"
                                            : typeof formData[key] === 'number'
                                            ? 'number'
                                            : 'text'
                                    }
                                    name={key}
                                    value={formData[key]}
                                    onChange={(e) => {
                                        if (key === "Date of Admission" || key === "Discharge Date") {
                                            handleDateChange(key, e.target.value);
                                        } else {
                                            handleChange(e);
                                        }
                                    }}
                                    step={typeof formData[key] === 'number' && !Number.isInteger(formData[key]) ? '0.01' : '1'}
                                    placeholder={`Enter ${key.toLowerCase()}`}
                                />
                            </label>
                        </div>
                    );
                })}

                <button type="submit" disabled={loading} className="submit-button">
                    {loading ? "Scoring Patient..." : "Assess Risk"}
                </button>
            </form>

            {/* Custom Ambulance Graphic */}
            <img 
                src="/ambulance.jpg" 
                alt="Ambulance" 
                className="form-ambulance-graphic" 
            />

            {error && <div className="error-box">Error: {error}</div>}

            {result && (
                <div className={`result-box ${result.status?.toLowerCase().replace(/\s+/g, '-') || ''}`}>
                    <h3>Assessment Results</h3>
                    <p><strong>Patient:</strong> {result.patient_name || formData["Patient Name"]}</p>
                    <p><strong>Status:</strong> {result.status}</p>
                    <p><strong>Prediction Code:</strong> {result.prediction}</p>
                    <p><strong>Confidence Probability:</strong> {(result.probability * 100).toFixed(2)}%</p>
                </div>
            )}
        </div>
    );
}
