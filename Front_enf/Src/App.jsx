import React from "react";
import PatientForm from "./components/PatientForm";
import BatchUpload from "./components/BatchUpload"; 
import AssessmentHistory from "./components/AssesmentHistory";

export default function App() {
  return (
    <div className="app-layout">
      {/* Left side spacer */}
      <div className="left-spacer"></div>

      {/* Center/Main Container with proper vertical spacing and overflow management */}
      <div className="main-content-wrapper" style={{ display: "flex", flexDirection: "column", gap: "40px", width: "100%", maxWidth: "850px", paddingBottom: "50px" }}>
        <PatientForm />
        
        <BatchUpload />

        {/* Audit Log rendered in its own clean card section */}
        <div style={{ background: "rgba(255, 255, 255, 0.95)", borderRadius: "12px", padding: "20px", boxShadow: "0 4px 15px rgba(0,0,0,0.2)" }}>
          <AssessmentHistory />
        </div>
      </div>

      {/* Right Side: Hospital Image with Moving Ambulance */}
      <div className="hospital-showcase-panel">
        <div className="ambulance-road"></div>
      </div>
    </div>
  );
}