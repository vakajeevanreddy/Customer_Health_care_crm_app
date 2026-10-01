import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const predictPatient = async (patientData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/predict`, patientData);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || "Failed to fetch prediction";
  }
};

export const predictBatchPatients = async (recordsArray) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/predict-batch`, recordsArray);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || "Failed to fetch batch prediction";
  }
};

export const fetchAssesmentHistory = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/assessment-history`);
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || "Failed to fetch assessment history";
    }
};
