
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("MODEL TRAINING WITH ALL AVAILABLE FEATURES")
print("=" * 70)

# Load data
df = pd.read_csv('data/icu_patient_data.csv')
print(f"\nTotal patients: {len(df)}")

# Use ALL numeric features except patient_id and target
exclude = ['patient_id', 'mortality_label']
all_features = [col for col in df.columns if col not in exclude and df[col].dtype in ['int64', 'float64']]

print(f"\nUsing {len(all_features)} features:")
for i, feat in enumerate(all_features):
    print(f"  {i+1}. {feat}")

X = df[all_features]
y = df['mortality_label']

# Check class distribution
survived = (y == 0).sum()
died = (y == 1).sum()
print(f"\nClass distribution:")
print(f"  Survived: {survived} ({survived/len(y)*100:.1f}%)")
print(f"  Died: {died} ({died/len(y)*100:.1f}%)")

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTraining set: {len(X_train)} patients")
print(f"Test set: {len(X_test)} patients")

# Define models with class balancing
models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    ),
    'Logistic Regression': LogisticRegression(
        class_weight='balanced',
        max_iter=2000,
        random_state=42,
        C=0.1
    )
}

try:
    from xgboost import XGBClassifier
    models['XGBoost'] = XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=survived/died,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
except:
    print("XGBoost not available")

results = []

print("\n" + "=" * 70)
print("TRAINING RESULTS WITH ALL FEATURES")
print("=" * 70)

for name, model in models.items():
    print(f"\n{'='*50}")
    print(f"Training {name}...")
    print(f"{'='*50}")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='roc_auc')
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    results.append({
        'Model': name,
        'Accuracy': f"{accuracy*100:.1f}%",
        'Precision': f"{precision*100:.1f}%",
        'Recall': f"{recall*100:.1f}%",
        'F1 Score': f"{f1*100:.1f}%",
        'ROC-AUC': f"{auc*100:.1f}%",
        'CV-AUC': f"{cv_scores.mean()*100:.1f}%"
    })
    
    print(f"\n📊 Metrics on Test Set:")
    print(f"   Accuracy:  {accuracy*100:.1f}%")
    print(f"   Precision: {precision*100:.1f}%")
    print(f"   Recall:    {recall*100:.1f}%")
    print(f"   F1 Score:  {f1*100:.1f}%")
    print(f"   ROC-AUC:   {auc*100:.1f}%")
    print(f"   5-Fold CV: {cv_scores.mean()*100:.1f}% (+/- {cv_scores.std()*100:.1f}%)")
    
    print(f"\n📋 Confusion Matrix:")
    print(f"   True Survived:  {cm[0,0]:4d}  |  False Death: {cm[0,1]:4d}")
    print(f"   False Survived: {cm[1,0]:4d}  |  True Death:  {cm[1,1]:4d}")
    
    # Calculate additional insights
    death_rate_pred = y_pred.mean() * 100
    actual_death_rate = y_test.mean() * 100
    print(f"\n📈 Prediction Insights:")
    print(f"   Model predicted death rate: {death_rate_pred:.1f}%")
    print(f"   Actual death rate: {actual_death_rate:.1f}%")
    
    # Save best model
    if auc > 0.7 and name == 'XGBoost':
        joblib.dump(model, 'models/best_model_all_features.pkl')
        joblib.dump(scaler, 'models/scaler.pkl')
        print(f"\n✅ Saved: models/best_model_all_features.pkl")

# Display results table
print("\n" + "=" * 70)
print("FINAL RESULTS COMPARISON")
print("=" * 70)

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Save results
results_df.to_csv('outputs/all_features_results.csv', index=False)
print(f"\n✅ Results saved: outputs/all_features_results.csv")

# Feature importance for Random Forest
if 'Random Forest' in models:
    print("\n" + "=" * 70)
    print("TOP 10 MOST IMPORTANT FEATURES")
    print("=" * 70)
    
    rf_model = models['Random Forest']
    importances = rf_model.feature_importances_
    feature_imp = [(all_features[i], importances[i]) for i in range(len(all_features))]
    feature_imp.sort(key=lambda x: x[1], reverse=True)
    
    for i, (feat, imp) in enumerate(feature_imp[:10]):
        print(f"  {i+1}. {feat}: {imp*100:.1f}%")
