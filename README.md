# Healthcare CRM with AWS, MLOps, RAG, and SLMs

A next-generation, HIPAA-compliant Healthcare CRM application that combines structured patient data management with predictive machine learning (MLOps) and secure Retrieval-Augmented Generation (RAG) powered by Small Language Models (SLMs) via Amazon Bedrock.

---

## Architecture Overview

```
[ Frontend (React/Next.js) ] 
       │
       ▼
[ API Gateway & AWS Lambda / FastAPI Backend ] 
       ├──► [ Amazon Aurora PostgreSQL ] (Structured Patient Records & CRM Logs)
       └──► [ Amazon OpenSearch Serverless ] ◄── (Vector Embeddings via Titan)
                     ▲
                     │ RAG Context
                     ▼
             [ Amazon Bedrock (Llama 3 / Mistral SLM) ]
```

* **Backend & API:** Serverless FastAPI running on AWS Lambda or Amazon ECS.
* **Database:** Amazon Aurora PostgreSQL for secure, relational patient data and CRM interactions.
* **MLOps & Predictive Modeling:** Automated SageMaker Pipelines tracking LightGBM/Scikit-learn models (e.g., readmission risk scores).
* **RAG & SLM:** Amazon Bedrock hosting lightweight Small Language Models combined with OpenSearch Serverless for clinical search and PII-guarded generation.

---

## Project Directory Structure

```text
healthcare-crm/
├── .github/workflows/          # CI/CD pipelines (GitHub Actions)
├── infrastructure/             # Infrastructure as Code (Terraform / AWS CDK)
├── backend/                    # Core CRM FastAPI Backend
├── mlops/                      # MLOps Pipelines (Preprocessing, Training, SageMaker DAGs)
├── rag_slm/                    # RAG Orchestration, Embedding generation, and Bedrock integration
├── frontend/                   # React/Next.js CRM Dashboard UI
├── tests/                      # Unit and integration test suites
└── README.md
```

---

## Getting Started & Prerequisites

### Prerequisites
* Python 3.10+
* Node.js 18+ (for frontend)
* AWS CLI configured with appropriate credentials
* Terraform (optional, for infrastructure provisioning)

### 1. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MLOps Pipeline Setup
To prepare data or trigger local pipeline test runs:
```bash
cd ../mlops/pipelines
python preprocessing.py
```

### 3. Running RAG & SLM Module
Ensure your AWS credentials have access to **Amazon Bedrock** and **Amazon OpenSearch Serverless**, then test the retriever module:
```bash
cd ../../rag_slm/bedrock
python -c "import prompt_templates; print('RAG module loaded successfully!')"
```

---

## Security & Compliance
* **Data Privacy:** All unstructured clinical notes pass through PII scrubbing and Bedrock Guardrails before reaching the SLM.
* **Encryption:** Enforced encryption at rest and in transit across all AWS services (Aurora, S3, OpenSearch).

---

## License
This project is proprietary and confidential.