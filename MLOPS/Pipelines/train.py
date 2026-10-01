import os
import joblib
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from Preprocessing import load_and_preprocess_data

def benchmark_models():
    dataset = r"C://Users//lenovo//OneDrive//Desktop//Health_Care_CRM//Data//archive//healthcare_dataset.csv"
    
    # 1. Load preprocessed data
    x_train, x_test, y_train, y_test, preprocessor = load_and_preprocess_data(dataset)
    
    # 2. Define a dictionary of models to test
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
        "Support Vector Classifier": SVC(probability=True, class_weight='balanced', random_state=42),
        "LightGBM": lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05, class_weight='balanced', random_state=42)
    }
    
    results = []
    trained_models = {}
    
    # 3. Train and evaluate each model
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        model.fit(x_train, y_train)
        
        y_pred = model.predict(x_test)
        y_prob = model.predict_proba(x_test)[:, 1]
            
        acc = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        
        results.append({
            "Model": name, 
            "Accuracy": acc, 
            "ROC-AUC": roc_auc
        })
        trained_models[name] = model
        
        print(f"{name} Results -> Accuracy: {acc:.4f} | ROC-AUC: {roc_auc:.4f}")

    # 4. Print Summary Comparison Table
    summary_df = pd.DataFrame(results).sort_values(by="ROC-AUC", ascending=False)
    print("\n" + "="*50)
    print("MODEL PERFORMANCE COMPARISON SUMMARY")
    print("="*50)
    print(summary_df.to_string(index=False))
    print("="*50)
    
    # 5. Automatically save the best model and preprocessor
    best_model_name = summary_df.iloc[0]["Model"]
    best_model = trained_models[best_model_name]
    print(f"\nBest Model by ROC-AUC: {best_model_name}. Saving artifacts...")
    
    # Create models directory inside MLOPS
    models_dir = r"C:\Users\lenovo\OneDrive\Desktop\Health_Care_CRM\MLOPS\models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Dump files using joblib
    joblib.dump(best_model, os.path.join(models_dir, "healthcare_model.pkl"))
    joblib.dump(preprocessor, os.path.join(models_dir, "preprocessor.pkl"))
    print(f"Artifacts successfully saved to: {models_dir}")

    return trained_models

if __name__ == "__main__":
    benchmark_models()