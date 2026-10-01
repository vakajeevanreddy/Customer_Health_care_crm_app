import React, { useState } from "react";
import { predictBatchPatients } from "../api/Api";
import './BatchUpload.css';

export default function BatchUpload() {
    const [batchResults, setBatchResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const parseCSV = (text) => {
        const lines = text.split("\n").map(line => line.trim()).filter(line => line.length > 0);
        if (lines.length < 2) throw new Error("CSV file must contain a header row and at least one data row.");
        
        const headers = lines[0].split(",").map(h => {
            let cleanH = h.trim().replace(/^"|"$/g, '');
            if (cleanH === "Name") return "Patient Name";
            return cleanH;
        });

        const rows = [];
        for (let i = 1; i < lines.length; i++) {
            const currLines = lines[i].split(",").map(val => val.trim().replace(/^"|"$/g, ''));
            const obj = {};
            headers.forEach((header, index) => {
                let val = currLines[index] !== undefined ? currLines[index] : "";
                if (["Age", "Room Number"].includes(header)) {
                    val = parseInt(val, 10) || 0;
                } else if (["Billing Amount"].includes(header)) {
                    val = parseFloat(val) || 0.0;
                }
                obj[header] = val;
            });
            rows.push(obj);
        }
        return rows;
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setLoading(true);
        setError(null);
        setBatchResults(null);

        const reader = new FileReader();
        reader.onload = async (event) => {
            try {
                const CSVText = event.target.result;
                const records = parseCSV(CSVText);

                const data = await predictBatchPatients(records);
                setBatchResults(data);
            } catch (err) {
                setError(err.message || err.toString());
            } finally {
                setLoading(false);
            }
        };
        reader.onerror = () => {
            setError("Failed to read the uploaded file.");
            setLoading(false);
        };
        reader.readAsText(file);
    };

    // Helper to calculate summary counts for the metrics cards
    const getRiskCounts = () => {
        if (!batchResults?.results) return { high: 0, moderate: 0, low: 0 };
        return batchResults.results.reduce((acc, curr) => {
            if (curr.status === "high-risk") acc.high++;
            else if (curr.status === "moderate-risk") acc.moderate++;
            else acc.low++;
            return acc;
        }, { high: 0, moderate: 0, low: 0 });
    };

    const riskCounts = getRiskCounts();

    return (
        <div className="batch-container" style={{ padding: "20px", maxWidth: "900px", margin: "0 auto" }}>
            <h2>Batch Patient Risk Scoring (Upload CSV)</h2>
            <p>Upload a CSV file containing columns matching your patient attributes to score multiple records at once.</p>
            
            <div className="form-group" style={{ margin: "20px 0" }}>
                <label>
                    Select Patient CSV File:
                    <input 
                        type="file" 
                        accept=".csv" 
                        onChange={handleFileUpload} 
                        disabled={loading} 
                        style={{ display: "block", marginTop: "10px" }}
                    />
                </label>
            </div>

            {loading && <p>Processing batch records through ML model...</p>}
            {error && <div className="error-box" style={{ color: "red", margin: "10px 0" }}>Error: {error}</div>}

            {batchResults && (
                <div className="batch-results">
                    <h3>Batch Results Summary</h3>
                    
                    {/* Summary Metrics Cards */}
                    <div style={{ display: "flex", gap: "15px", margin: "15px 0" }}>
                        <div style={{ flex: 1, background: "#f8f9fa", padding: "12px", borderRadius: "6px", borderLeft: "4px solid #222" }}>
                            <h4>Total Processed</h4>
                            <p style={{ fontSize: "20px", fontWeight: "bold" }}>{batchResults.total_processed}</p>
                        </div>
                        <div style={{ flex: 1, background: "#ffe6e6", padding: "12px", borderRadius: "6px", borderLeft: "4px solid #cc0000" }}>
                            <h4 style={{ color: "#cc0000" }}>High Risk</h4>
                            <p style={{ fontSize: "20px", fontWeight: "bold", color: "#cc0000" }}>{riskCounts.high}</p>
                        </div>
                        <div style={{ flex: 1, background: "#fff5cc", padding: "12px", borderRadius: "6px", borderLeft: "4px solid #b38600" }}>
                            <h4 style={{ color: "#b38600" }}>Moderate Risk</h4>
                            <p style={{ fontSize: "20px", fontWeight: "bold", color: "#b38600" }}>{riskCounts.moderate}</p>
                        </div>
                        <div style={{ flex: 1, background: "#e6f9e6", padding: "12px", borderRadius: "6px", borderLeft: "4px solid #006600" }}>
                            <h4 style={{ color: "#006600" }}>Low Risk</h4>
                            <p style={{ fontSize: "20px", fontWeight: "bold", color: "#006600" }}>{riskCounts.low}</p>
                        </div>
                    </div>

                    <div style={{ maxHeight: "400px", overflowY: "auto", marginTop: "15px" }}>
                        <table border="1" cellPadding="8" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
                            <thead>
                                <tr style={{ background: "#222", color: "#fff" }}>
                                    <th>Row</th>
                                    <th>Prediction Code</th>
                                    <th>Probability</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {batchResults.results && batchResults.results.map((res) => {
                                    // 3-tier styling configuration
                                    const isHigh = res.status === "high-risk";
                                    const isMod = res.status === "moderate-risk";
                                    
                                    const bgColor = isHigh ? "#ffe6e6" : isMod ? "#fff5cc" : "#e6f9e6";
                                    const textColor = isHigh ? "#cc0000" : isMod ? "#b38600" : "#006600";

                                    return (
                                        <tr key={res.row_index}>
                                            <td>{res.row_index + 1}</td>
                                            <td>{res.Prediction}</td>
                                            <td>{(res.Probability * 100).toFixed(2)}%</td>
                                            <td>
                                                <span style={{ 
                                                    padding: "4px 8px", 
                                                    borderRadius: "4px",
                                                    background: bgColor,
                                                    color: textColor,
                                                    fontWeight: "bold"
                                                }}>
                                                    {res.status}
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}