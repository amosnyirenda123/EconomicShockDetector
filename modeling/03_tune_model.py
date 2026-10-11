import pandas as pd
import numpy as np
from pathlib import Path
import mlflow
import mlflow.sklearn
import json
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import recall_score, make_scorer
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# --- Configuration ---
PROCESSED_DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'
MODELS_DIR = Path(__file__).parent.parent / 'models'
MLFLOW_TRACKING_URI = f"sqlite:///{Path(__file__).parent.parent / 'mlflow.db'}"
EXPERIMENT_NAME = "WorldBank_GDP_Shock_Modeling"
TARGET = 'gdp_shock'
RANDOM_STATE = 42

SKOPS_TRUSTED_TYPES = [
    # imblearn components
    "imblearn.pipeline.Pipeline",
    "imblearn.over_sampling._smote.base.SMOTE",
    "imblearn.under_sampling._prototype_selection._random_under_sampler.RandomUnderSampler",
    
    # sklearn tree-based models
    "sklearn.tree._tree.Tree",
    
    # XGBoost
    "xgboost.core.Booster",
    "xgboost.sklearn.XGBClassifier",
    
    # MLP (likely needed)
    "sklearn.neural_network._multilayer_perceptron.MLPClassifier",
    
    # LogisticRegression solver internals (saga/lbfgs may reference these)
    "sklearn.linear_model._sag._sag_fit",
    "sklearn.linear_model._sag_fast",
]

def setup_mlflow():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

def main():
    print("--- Starting Hyperparameter Tuning with MLflow ---")
    setup_mlflow()

    train_df = pd.read_csv(PROCESSED_DATA_DIR / 'train.csv')
    val_df = pd.read_csv(PROCESSED_DATA_DIR / 'validation.csv')
    
    FEATURES = [c for c in train_df.columns if c != TARGET]
    X_train, y_train = train_df[FEATURES].values, train_df[TARGET].values
    X_val, y_val = val_df[FEATURES].values, val_df[TARGET].values

    # Load results from previous step to pick the best model
    modeling_results = pd.read_csv(PROCESSED_DATA_DIR / 'modeling_results.csv')
    best_row = modeling_results.sort_values(['recall_mean', 'f1_mean'], ascending=False).iloc[0]
    best_model_name, best_strategy_name = best_row['Modèle'], best_row['Stratégie']
    print(f"Best combination from baseline: {best_model_name} + {best_strategy_name}")

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    # Define the model and parameter grid
    param_grids = {
        'XGBoost': {
            'model__n_estimators': [300, 500, 700],
            'model__max_depth': [3, 5, 7],
            'model__learning_rate': [0.01, 0.05, 0.1],
            'model__subsample': [0.7, 0.8, 1.0],
            'model__colsample_bytree': [0.7, 0.8, 1.0],
        }
    }
    
    models = {
        'XGBoost': XGBClassifier(scale_pos_weight=scale_pos_weight, eval_metric='logloss', random_state=RANDOM_STATE, verbosity=0)
    }
    
    samplers = {
        'Undersampling': RandomUnderSampler(random_state=RANDOM_STATE),
        'SMOTE': SMOTE(random_state=RANDOM_STATE),
    }

    model = models[best_model_name]
    param_grid = param_grids[best_model_name]
    sampler = samplers.get(best_strategy_name)

    if sampler:
        pipeline = ImbPipeline([('sampler', sampler), ('model', model)])
    else:
        pipeline = ImbPipeline([('model', model)])
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    recall_scorer = make_scorer(recall_score, pos_label=1, zero_division=0)

    with mlflow.start_run(run_name=f"Tuning_{best_model_name}_{best_strategy_name}") as parent_run:
        mlflow.log_param("model_name", best_model_name)
        mlflow.log_param("strategy_name", best_strategy_name)
        
        search = RandomizedSearchCV(
            estimator=pipeline, param_distributions=param_grid, n_iter=30,
            scoring=recall_scorer, cv=cv, n_jobs=-1,
            random_state=RANDOM_STATE, verbose=1, refit=True
        )
        search.fit(X_train, y_train)

        mlflow.log_params(search.best_params_)
        mlflow.log_metric("best_cv_recall", search.best_score_)
        
        print(f"Best CV Recall: {search.best_score_:.4f}")

        # Log the best model as a child run with the 'best' tag
        with mlflow.start_run(run_name="BestModel", nested=True) as best_run:
            best_estimator = search.best_estimator_
            
            y_val_pred = best_estimator.predict(X_val)
            val_recall = recall_score(y_val, y_val_pred, pos_label=1)
            
            mlflow.log_metric("val_recall", val_recall)
            mlflow.set_tag("model_type", "tuned_final")
            
            signature = mlflow.models.infer_signature(X_train, best_estimator.predict(X_train))
            mlflow.sklearn.log_model(best_estimator, "model", signature=signature, serialization_format="cloudpickle")

            # Save locally as well (as in your notebook)
            joblib.dump(best_estimator, MODELS_DIR / 'tuned_model.joblib')
            
            tuning_meta = {
                'best_model': best_model_name,
                'best_strategy': best_strategy_name,
                'best_params': search.best_params_,
                'best_cv_recall': search.best_score_,
                'val_recall': val_recall,
                'mlflow_run_id': best_run.info.run_id,
            }
            with open(MODELS_DIR / 'tuning_meta.json', 'w') as f:
                json.dump(tuning_meta, f, indent=2, default=str)
            mlflow.log_artifact(MODELS_DIR / 'tuning_meta.json')


    print("--- Hyperparameter Tuning Finished ---")

if __name__ == '__main__':
    main()