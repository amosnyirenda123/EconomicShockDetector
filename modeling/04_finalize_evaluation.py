import pandas as pd
import numpy as np
from pathlib import Path
import mlflow
import mlflow.sklearn
import json
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    recall_score, precision_score, f1_score, average_precision_score,
    roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve
)

# --- Configuration ---
PROCESSED_DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'
MODELS_DIR = Path(__file__).parent.parent / 'models'
MLFLOW_TRACKING_URI = f"sqlite:///{Path(__file__).parent.parent / 'mlflow.db'}"
EXPERIMENT_NAME = "WorldBank_GDP_Shock_Modeling"
REGISTERED_MODEL_NAME = "WorldBank_GDP_Shock_Classifier"
TARGET = 'gdp_shock'

# --- Cost Matrix ---
COST_FN = 1000  # Cost of a False Negative (missing a shock)
COST_FP = 1     # Cost of a False Positive (false alarm)

def setup_mlflow():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

def find_optimal_threshold(y_true, y_proba, costs=range(1, 100)):
    """Finds the threshold that minimizes the business cost."""
    thresholds = np.arange(0.01, 1.0, 0.01)
    best_threshold, min_cost = 0.5, float('inf')
    
    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        total_cost = COST_FN * fn + COST_FP * fp
        if total_cost < min_cost:
            min_cost = total_cost
            best_threshold = t
    return best_threshold, min_cost

def plot_and_log_artifacts(y_true, y_proba, threshold):
    """Generates and saves plots for evaluation."""
    # Plot 1: Confusion Matrix
    y_pred = (y_proba >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Predicted Normal', 'Predicted Shock'],
                yticklabels=['Actual Normal', 'Actual Shock'])
    plt.title(f'Confusion Matrix (Threshold = {threshold:.2f})')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    cm_path = MODELS_DIR / 'final_confusion_matrix.png'
    plt.savefig(cm_path)
    plt.close()
    mlflow.log_artifact(cm_path)

    # Plot 2: ROC and PR Curves
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    axes[0].plot(fpr, tpr, color='steelblue', linewidth=2, label=f'ROC-AUC = {roc_auc_score(y_true, y_proba):.3f}')
    axes[0].plot([0, 1], [0, 1], 'k--', alpha=0.4, label='Random')
    axes[0].set_xlabel('False Positive Rate'); axes[0].set_ylabel('True Positive Rate')
    axes[0].set_title('ROC Curve'); axes[0].legend(); axes[0].grid(alpha=0.3)
    
    prec_curve, rec_curve, _ = precision_recall_curve(y_true, y_proba)
    baseline_pr = y_true.mean()
    axes[1].plot(rec_curve, prec_curve, color='darkorange', linewidth=2, label=f'PR-AUC = {average_precision_score(y_true, y_proba):.3f}')
    axes[1].axhline(baseline_pr, color='gray', linestyle='--', label=f'Baseline = {baseline_pr:.3f}')
    axes[1].set_xlabel('Recall'); axes[1].set_ylabel('Precision')
    axes[1].set_title('Precision-Recall Curve'); axes[1].legend(); axes[1].grid(alpha=0.3)
    plt.tight_layout()
    curves_path = MODELS_DIR / 'final_roc_pr_curves.png'
    plt.savefig(curves_path)
    plt.close()
    mlflow.log_artifact(curves_path)

def main():
    print("--- Starting Final Evaluation & Model Registration ---")
    setup_mlflow()

    test_df = pd.read_csv(PROCESSED_DATA_DIR / 'test.csv')
    FEATURES = [c for c in test_df.columns if c != TARGET]
    X_test, y_test = test_df[FEATURES].values, test_df[TARGET].values

    # Load the tuned model
    pipeline = joblib.load(MODELS_DIR / 'tuned_model.joblib')
    with open(MODELS_DIR / 'tuning_meta.json') as f:
        tuning_meta = json.load(f)

    # Get probabilities
    y_test_proba = pipeline.predict_proba(X_test)[:, 1]

    # Find the optimal business threshold
    optimal_threshold, min_cost = find_optimal_threshold(y_test, y_test_proba)
    print(f"Optimal business threshold found: {optimal_threshold:.2f} (Cost: {min_cost})")

    # Evaluate final metrics
    y_pred_optimal = (y_test_proba >= optimal_threshold).astype(int)
    final_metrics = {
        "recall": float(recall_score(y_test, y_pred_optimal)),
        "precision": float(precision_score(y_test, y_pred_optimal)),
        "f1": float(f1_score(y_test, y_pred_optimal)),
        "roc_auc": float(roc_auc_score(y_test, y_test_proba)),
        "pr_auc": float(average_precision_score(y_test, y_test_proba)),
        "business_cost": float(min_cost),
        "optimal_threshold": float(optimal_threshold),
    }
    print("Final Test Metrics:", final_metrics)

    # --- Log and Register the Final Model (single active run) ---
    with mlflow.start_run(run_name="Final_Registered_Model") as run:
        mlflow.log_param("tuned_model_run_id", tuning_meta['mlflow_run_id'])
        mlflow.log_metrics(final_metrics)

        # Plots are generated AND logged inside the run
        plot_and_log_artifacts(y_test, y_test_proba, optimal_threshold)

        # Save the final payload locally and log it
        final_payload = {
            'model': pipeline,
            'optimal_threshold': optimal_threshold,
            'feature_names': FEATURES,
            'test_metrics': final_metrics,
            'cost_matrix': {'cost_fn': COST_FN, 'cost_fp': COST_FP}
        }
        final_model_path = MODELS_DIR / 'final_model.joblib'
        joblib.dump(final_payload, final_model_path)
        mlflow.log_artifact(final_model_path)

        # Log the model with cloudpickle and register it
        signature = mlflow.models.infer_signature(X_test, y_test_proba)
        mlflow.sklearn.log_model(
            sk_model=pipeline,
            name="model",
            signature=signature,
            registered_model_name=REGISTERED_MODEL_NAME,
            input_example=X_test[:5],
            metadata={"optimal_threshold": optimal_threshold},
            serialization_format="cloudpickle",
        )

        print(f"\nModel '{REGISTERED_MODEL_NAME}' registered successfully.")
        print(f"Run ID for final model: {run.info.run_id}")

    print("--- Final Evaluation & Model Registration Finished ---")