import React, { useState, useEffect } from "react";
import { fetchAssesmentHistory } from "../api/Api";

export default function AssessmentHistory() {
    const [historyData, setHistoryData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const loadHistory = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await fetchAssesmentHistory();
            setHistoryData(data);
        } catch (err) {
            setError(err.toString());
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadHistory();
    }, []);

    return (
        <div className="history_container" style={{ padding: "20px", maxWidth: "850px", margin: "0 auto", background: "#fff", borderRadius: "8px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)", color: "#000" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <h2 style={{ color: "#000", margin: 0 }}>Patient Assessment Audit Log</h2>
                <button 
                    onClick={loadHistory} 
                    disabled={loading} 
                    style={{ padding: "8px 16px", background: "#0066cc", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                >
                    {loading ? "Refreshing..." : "Refresh Log"}
                </button>
            </div>

            {error && <div style={{ color: "red", margin: "10px 0" }}>Error: {error}</div>}

            <div>
                <p style={{ color: "#000" }}><strong>Total Recorded Assessments:</strong> {historyData?.total_records || 0}</p>
                <div style={{ maxHeight: "450px", overflowY: "auto", marginTop: "15px", border: "1px solid #ddd", borderRadius: "6px" }}>
                    <table border="1" cellPadding="8" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", background: "#fff", color: "#000" }}>
                        <thead>
                            <tr style={{ background: "#222", color: "#fff" }}>
                                <th>Timestamp</th>
                                <th>Patient Name</th>
                                <th>Age</th>
                                <th>Condition</th>
                                <th>Billing</th>
                                <th>Probability</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {!historyData?.history || historyData.history.length === 0 ? (
                                <tr>
                                    <td colSpan="7" style={{ textAlign: "center", padding: "20px", color: "#000" }}>
                                        {loading ? "Loading history..." : "No Previous Assessment Found. Try submitting a Patient Form!"}
                                    </td>
                                </tr>
                            ) : (
                                historyData.history.slice().reverse().map((row, index) => {
                                    const isHigh = row.Risk_Status === "high-risk";
                                    const isMod = row.Risk_Status === "moderate-risk";
                                    
                                    const bg = isHigh ? "#ffe6e6" : isMod ? "#fff5cc" : "#e6f9e6";
                                    const fg = isHigh ? "#cc0000" : isMod ? "#b38600" : "#006600";
                                    
                                    {/* Robust fallback check for all possible name column variations */}
                                    const patientName = row["Patient Name"] || row["patient_name"] || row["Patient_Name"] || row["Name"] || row["name"] || "N/A";

                                    return (
                                        <tr key={index} style={{ color: "#000" }}>
                                            <td style={{ fontSize: "12px", color: "#000" }}>{row.Assessment_Timestamp}</td>
                                            <td style={{ color: "#000" }}>{patientName}</td>
                                            <td style={{ color: "#000" }}>{row.Age}</td>
                                            <td style={{ color: "#000" }}>{row["Medical Condition"]}</td>
                                            <td style={{ color: "#000" }}>${row["Billing Amount"]}</td>
                                            <td style={{ color: "#000" }}>{(row.Probability * 100).toFixed(2)}%</td>
                                            <td>
                                                <span style={{ padding: "3px 6px", borderRadius: "4px", background: bg, color: fg, fontWeight: "bold" }}>
                                                    {row.Risk_Status}
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}