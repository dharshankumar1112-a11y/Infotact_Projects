import pandas as pd
import numpy as np
import joblib
import os
import warnings
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score, recall_score, precision_score, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

# Ignore warnings for cleaner output
warnings.filterwarnings('ignore')

# ===================================================================
# 1. DATA LOADING & PREPARATION
# ===================================================================
print("Loading dataset...")
# Using the filename you provided
df = pd.read_csv('week1-CleanedData.csv')

# --- DATA LEAKAGE PREVENTION ---
# We must exclude failure type indicators (TWF, HDF, etc.) 
# because they are direct components of the 'failure' target.
leakage_cols = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
metadata_cols = ['UDI', 'Product ID', 'machine_id', 'timestamp']

# Encode the 'Type' categorical variable
df = pd.get_dummies(df, columns=['Type'], drop_first=True)

# Select features: Exclude target, metadata, and leakage columns
exclude_all = leakage_cols + metadata_cols + ['failure']
feature_cols = [col for col in df.columns if col not in exclude_all]

X = df[feature_cols].fillna(0)
y = df['failure']

print(f"Dataset shape: {df.shape}")
print(f"Selected {len(feature_cols)} features for training.")
print(f"Failure Rate: {y.mean():.2%}")

# Stratified split to preserve the minority class ratio
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ===================================================================
# 2. BASELINE MODEL: Logistic Regression (Scaled)
# ===================================================================
print("\n" + "="*70)
print("1. ESTABLISHING BASELINE (Logistic Regression)")
print("="*70)

# Logistic Regression needs scaling for proper performance
baseline_pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000))
])

baseline_pipe.fit(X_train, y_train)
y_pred_baseline = baseline_pipe.predict(X_test)

baseline_f1 = f1_score(y_test, y_pred_baseline)
baseline_recall = recall_score(y_test, y_pred_baseline)

print("\nBaseline Results:")
print(f"Recall:   {baseline_recall:.4f}")
print(f"F1-Score: {baseline_f1:.4f}")

# ===================================================================
# 3. RANDOM FOREST HYPERPARAMETER TUNING
# ===================================================================
print("\n" + "="*70)
print("2. TRAINING RANDOM FOREST (RandomizedSearch)")
print("="*70)

rf_params = {
    'n_estimators': [100, 200, 300, 500],
    'max_depth': [10, 20, 30, None],
    'min_samples_leaf': [1, 2, 4],
    'class_weight': ['balanced', 'balanced_subsample']
}

rf_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_distributions=rf_params,
    n_iter=20,
    cv=5,
    scoring='f1', # Optimizing for F1-Score as requested
    n_jobs=-1,
    random_state=42,
    verbose=1
)

rf_search.fit(X_train, y_train)
rf_best = rf_search.best_estimator_
y_pred_rf = rf_best.predict(X_test)

# ===================================================================
# 4. XGBOOST HYPERPARAMETER TUNING
# ===================================================================
print("\n" + "="*70)
print("3. TRAINING XGBOOST (High Performance)")
print("="*70)

# Calculate ratio for scale_pos_weight to handle imbalance
ratio = (y_train == 0).sum() / (y_train == 1).sum()

xgb_params = {
    'n_estimators': [100, 200, 300, 500],
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'subsample': [0.7, 0.8, 1.0],
    'scale_pos_weight': [ratio] # Heavily weights the 'failure' class
}

xgb_search = RandomizedSearchCV(
    XGBClassifier(random_state=42, eval_metric='logloss'),
    param_distributions=xgb_params,
    n_iter=20,
    cv=5,
    scoring='f1',
    n_jobs=-1,
    random_state=42,
    verbose=1
)

xgb_search.fit(X_train, y_train)
xgb_best = xgb_search.best_estimator_

# OPTIMIZATION: Custom Threshold to prioritize RECALL
# By lowering the threshold, we catch more failures (Minimizing False Negatives)
y_probs_xgb = xgb_best.predict_proba(X_test)[:, 1]
y_pred_xgb_tuned = (y_probs_xgb > 0.35).astype(int)

# ===================================================================
# 5. FINAL PERFORMANCE COMPARISON
# ===================================================================
print("\n" + "="*70)
print("FINAL PERFORMANCE SUMMARY")
print("="*70)

results = pd.DataFrame({
    'Model': ['Baseline (LogReg)', 'Random Forest', 'XGBoost (Recall-Tuned)'],
    'Accuracy': [
        accuracy_score(y_test, y_pred_baseline),
        accuracy_score(y_test, y_pred_rf),
        accuracy_score(y_test, y_pred_xgb_tuned)
    ],
    'Recall': [
        baseline_recall,
        recall_score(y_test, y_pred_rf),
        recall_score(y_test, y_pred_xgb_tuned)
    ],
    'F1-Score': [
        baseline_f1,
        f1_score(y_test, y_pred_rf),
        f1_score(y_test, y_pred_xgb_tuned)
    ]
})

print(results.to_string(index=False))

# Identify if XGBoost beat the baseline
if results.loc[2, 'F1-Score'] > results.loc[0, 'F1-Score']:
    print("\n🏆 SUCCESS: XGBoost beat the Baseline F1-Score!")

# ===================================================================
# 6. SAVING OUTPUTS
# ===================================================================
# Define your specific save path
output_path = 'Output'

if not os.path.exists(output_path):
    os.makedirs(output_path)

# Save the best model
joblib.dump(xgb_best, os.path.join(output_path, 'best_xgb_model.pkl'))

# Save Feature Importance
importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': xgb_best.feature_importances_
}).sort_values(by='importance', ascending=False)

importance.to_csv(os.path.join(output_path, 'feature_importance.csv'), index=False)
results.to_csv(os.path.join(output_path, 'model_comparison.csv'), index=False)

print(f"\n✅ All files (Model, Importance, Comparison) saved to: {output_path}")

# ===================================================================
# 7. WEEK 3: INTERPRETABILITY & TRUST (XAI)
# ===================================================================
print("\n" + "="*70)
print("WEEK 3: INTERPRETABILITY & TRUST (XAI)")
print("="*70)

import shap
import matplotlib.pyplot as plt

# Load the best model (already saved in Week 2)
model = joblib.load(os.path.join(output_path, 'best_xgb_model.pkl'))

# Calculate SHAP values for the test set
print("Calculating SHAP values...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Force Plots (Local Explanations)
print("Generating Force Plots for sample predictions...")

for i in range(3):  # first 3 samples
    force_plot = shap.force_plot(
        explainer.expected_value,
        shap_values[i, :],
        X_test.iloc[i, :]
    )
    shap.save_html(
        os.path.join(output_path, f'force_plot_sample_{i}.html'),
        force_plot
    )
print(f"✅ Force plots saved to {output_path}")

# Summary Plot (Global Explanations)
print("Generating Summary Plot...")
plt.figure()
shap.summary_plot(shap_values, X_test, show=False)
plt.savefig(os.path.join(output_path, 'summary_plot.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✅ Summary plot saved.")

# Dependence Plots (Top Features)
print("Generating Dependence Plots for top features...")
shap_importance = np.abs(shap_values).mean(0)
top_features = pd.Series(shap_importance, index=X_test.columns).nlargest(5).index.tolist()

for feature in top_features:
    plt.figure()
    shap.dependence_plot(feature, shap_values, X_test, show=False)
    plt.savefig(os.path.join(output_path, f'dependence_{feature}.png'),
                dpi=300, bbox_inches='tight')
    plt.close()
print("✅ Dependence plots saved.")

# Validation Notes
print("\nValidation against physical expectations:")
print("- High temperature should correlate with higher SHAP values (failure risk).")
print("- High vibration/torque should correlate with higher SHAP values.")
print("- Low rotational speed may indicate higher risk (bearing wear).")
print("Check the dependence plots to confirm these trends.")