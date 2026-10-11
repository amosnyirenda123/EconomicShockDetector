import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import sys


sys.path.append(str(Path(__file__).parent))
from src.preprocessing import GroupMedianImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, RobustScaler
import joblib


DATA_PATH = Path(__file__).parent.parent / 'data' / 'raw' / 'dataset.csv'
PROCESSED_DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'
MODELS_DIR = Path(__file__).parent.parent / 'models'
TARGET = 'gdp_shock'
RANDOM_STATE = 42

def create_preprocessing_pipeline(df_preprocessed):
    """Defines the full preprocessing pipeline based on decisions from the notebook."""
  
    nominal_categorical_cols = ['region', 'income_group', 'lending_type']
    ordinal_categorical_cols = ['is_crisis_decade']
    binary_passthrough_cols = ['high_external_debt']
    log_passthrough_cols = ['gdp_per_capita_log']
    passthrough_cols = binary_passthrough_cols + log_passthrough_cols

  
    excluded_cols = ['gdp_per_capita', 'gdp_per_capita_log'] + nominal_categorical_cols + ordinal_categorical_cols + passthrough_cols
    numeric_cols = [col for col in df_preprocessed.select_dtypes(include=['float64']).columns if col not in excluded_cols]
    
    
    numeric_imputer_input_cols = numeric_cols + ['income_group']

    numeric_pipeline = Pipeline(steps=[
        ('imputer', GroupMedianImputer(group_col='income_group', feature_cols=numeric_cols)),
        ('scaler', RobustScaler()),
    ])

    nominal_categorical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])

    ordinal_categorical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OrdinalEncoder(categories=[['1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']])),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('numeric', numeric_pipeline, numeric_imputer_input_cols),
            ('nominal_categorical', nominal_categorical_pipeline, nominal_categorical_cols),
            ('ordinal_categorical', ordinal_categorical_pipeline, ordinal_categorical_cols),
            ('passthrough', 'passthrough', passthrough_cols),
        ],
        remainder='drop',
    )
    return preprocessor

def main():
    print("--- Starting Data Preparation ---")
    df = pd.read_csv(DATA_PATH)
    print(f"Raw data shape: {df.shape}")

   
    high_missing_cols = ['domestic_credit_pct', 'govt_debt_pct_gdp']
    df_preprocessed = df.drop(columns=high_missing_cols)
    print(f"Shape after dropping high-missing columns: {df_preprocessed.shape}")


    df_preprocessed = df_preprocessed.dropna(subset=['gdp_per_capita']).copy()
    print(f"Shape after dropping gdp_per_capita NaN rows: {df_preprocessed.shape}")

    df_preprocessed['gdp_per_capita_log'] = np.log(df_preprocessed['gdp_per_capita'])
    df_preprocessed['high_external_debt'] = (df_preprocessed['external_debt_pct'] > 80).astype(int)
    print("Added engineered features: gdp_per_capita_log, high_external_debt")

  
    leakage_cols = ['gdp_growth', 'gdp_growth_lag1', 'gdp_growth_delta']
    df_preprocessed = df_preprocessed.drop(columns=leakage_cols)
    print(f"Shape after dropping leakage columns: {df_preprocessed.shape}")

  
    identifier_cols = ['country', 'country_name', 'year']
    X = df_preprocessed.drop(columns=identifier_cols + [TARGET])
    y = df_preprocessed[TARGET].copy()

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=RANDOM_STATE)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_STATE)
    print(f"Splits created: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")


    preprocessor = create_preprocessing_pipeline(df_preprocessed)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_val_processed = preprocessor.transform(X_val)
    X_test_processed = preprocessor.transform(X_test)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    feature_names = preprocessor.get_feature_names_out()
    
    train_df = pd.DataFrame(X_train_processed, columns=feature_names)
    train_df[TARGET] = y_train.values
    train_df.to_csv(PROCESSED_DATA_DIR / 'train.csv', index=False)

    val_df = pd.DataFrame(X_val_processed, columns=feature_names)
    val_df[TARGET] = y_val.values
    val_df.to_csv(PROCESSED_DATA_DIR / 'validation.csv', index=False)

    test_df = pd.DataFrame(X_test_processed, columns=feature_names)
    test_df[TARGET] = y_test.values
    test_df.to_csv(PROCESSED_DATA_DIR / 'test.csv', index=False)
    
    joblib.dump(preprocessor, MODELS_DIR / 'preprocessor.joblib')

    print(f"Processed data saved to {PROCESSED_DATA_DIR}")
    print(f"Preprocessor saved to {MODELS_DIR / 'preprocessor.joblib'}")
    print("--- Data Preparation Finished ---")

if __name__ == '__main__':
    main()