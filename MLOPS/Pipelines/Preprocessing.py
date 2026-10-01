import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def load_and_preprocess_data(file_path : str):
    print(f"Loading Data Set : {file_path}")
    df = pd.read_csv(file_path)

    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"])
    df["Length_to_Stay"] = (df["Discharge Date"] - df["Date of Admission"]).dt.days

    drop_cols = ['Name' , 'Date of Admission' , 'Discharge Date' , 'Doctor' ,'Hospital' , 'Room Number']
    df = df.drop(columns = drop_cols , errors = 'ignore')

    if 'Test Results' in df.columns:
        df['Target'] = df['Test Results'].apply(lambda x: 1 if str(x).strip().lower() == 'abnormal' else 0)
        df = df.drop(columns=['Test Results'])
        print("DEBUG: 'Test Results' successfully dropped! Current columns count:", len(df.columns))
    #sep the features and target
    X = df.drop(columns = ['Target'])
    y = df['Target']

    numeric_features = X.select_dtypes(include = ['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include = ['category','object']).columns.tolist()

    print(f"Numerical Features : {numeric_features}")
    print(f"Categorical_features: {categorical_features}")

    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore',sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[('num' , numeric_transformer , numeric_features),
                      ('cat' , categorical_transformer , categorical_features)]
    )

    x_train,x_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    x_train_preprocessed = preprocessor.fit_transform(x_train)
    x_test_preprocessed = preprocessor.fit_transform(x_test)
    print("Preprocessing completed successfully!")
    print(f"X_train processed shape: {x_train_preprocessed.shape}")
    print(f"X_test processed shape: {x_test_preprocessed.shape}")
    
    return x_train_preprocessed, x_test_preprocessed, y_train, y_test, preprocessor

if __name__ == "__main__":
    # Use the absolute path to your dataset
    dataset_path = r"C://Users//lenovo//OneDrive//Desktop//Health_Care_CRM//Data//archive//healthcare_dataset.csv"
    load_and_preprocess_data(dataset_path)






