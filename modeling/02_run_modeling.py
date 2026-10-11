import pandas as pd
import numpy as np
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import recall_score, precision_score, f1_score, average_precision_score, make_scorer
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# --- Configuration ---
PROCESSED_DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'
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

def get_models_and_strategies(scale_pos_weight):
    MODELS = {
        'LogisticRegression': LogisticRegression(class_weight='balanced', max_iter=5000, solver='saga', random_state=RANDOM_STATE),
        'DecisionTree': DecisionTreeClassifier(class_weight='balanced', random_state=RANDOM_STATE),
        'XGBoost': XGBClassifier(scale_pos_weight=scale_pos_weight, eval_metric='logloss', random_state=RANDOM_STATE, verbosity=0),
        'MLP': MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=500, early_stopping=True, random_state=RANDOM_STATE),
    }
    STRATEGIES = {
        'Baseline (class_weight)': None,
        'SMOTE': SMOTE(random_state=RANDOM_STATE),
        'Undersampling': RandomUnderSampler(random_state=RANDOM_STATE),
    }
    return MODELS, STRATEGIES

def main():
    print("--- Starting Baseline Modeling with MLflow ---")
    setup_mlflow()

    train_df = pd.read_csv(PROCESSED_DATA_DIR / 'train.csv')
    FEATURES = [c for c in train_df.columns if c != TARGET]
    X_train = train_df[FEATURES].values
    y_train = train_df[TARGET].values

    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / pos_count
    print(f"Calculated scale_pos_weight: {scale_pos_weight:.2f}")

    MODELS, STRATEGIES = get_models_and_strategies(scale_pos_weight)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        'recall': make_scorer(recall_score, pos_label=1, zero_division=0),
        'precision': make_scorer(precision_score, pos_label=1, zero_division=0),
        'f1': make_scorer(f1_score, pos_label=1, zero_division=0),
        'pr_auc': make_scorer(average_precision_score, response_method='predict_proba'),
    }
    
    results = []

    for model_name, model in MODELS.items():
        for strategy_name, sampler in STRATEGIES.items():
            run_name = f"{model_name} | {strategy_name}"
            print(f"  Running: {run_name}")
            
            with mlflow.start_run(run_name=run_name) as run:
                # Log model and strategy names as parameters
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("strategy_name", strategy_name)
                if model_name == 'XGBoost':
                    mlflow.log_param("scale_pos_weight", scale_pos_weight)

                if sampler is not None:
                    pipeline = ImbPipeline([('sampler', sampler), ('model', model)])
                else:
                    pipeline = ImbPipeline([('model', model)])

                cv_scores = cross_validate(pipeline, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1, error_score='raise')

                # Log mean and std of metrics
                metrics = {}
                for metric in ['recall', 'precision', 'f1', 'pr_auc']:
                    mean_score = cv_scores[f'test_{metric}'].mean()
                    std_score = cv_scores[f'test_{metric}'].std()
                    metrics[f'{metric}_mean'] = mean_score
                    metrics[f'{metric}_std'] = std_score
                    mlflow.log_metric(f"{metric}_mean", mean_score)
                    mlflow.log_metric(f"{metric}_std", std_score)

                # Log the model signature and the model itself
                # Note: We are logging the model trained on a single fold for now as an example.
                # In the tuning stage, we will log the final refitted model.
                pipeline.fit(X_train, y_train)
                signature = mlflow.models.infer_signature(X_train, pipeline.predict(X_train))
                mlflow.sklearn.log_model(
                    pipeline,
                    "model",
                    signature=signature,
                    serialization_format="cloudpickle",
                    
                )

                results.append({
                    'run_id': run.info.run_id,
                    'Modèle': model_name,
                    'Stratégie': strategy_name,
                    **metrics
                })
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(PROCESSED_DATA_DIR / 'modeling_results.csv', index=False)
    
    print("\n--- Baseline Modeling Finished ---")
    print(results_df.sort_values(by=['recall_mean', 'f1_mean'], ascending=False).to_string())


if __name__ == '__main__':
    main()