from flask import Flask, request, jsonify
import joblib
import numpy as np
import shap

app = Flask(__name__)

# Load trained model
model = joblib.load("Output/best_xgb_model.pkl")

# SHAP explainer
explainer = shap.TreeExplainer(model)

# ---- BASE FEATURES (Postman sends these) ----
BASE_FEATURES = [
    "air_temp",
    "process_temp",
    "rotational_speed",
    "torque",
    "tool_wear"
]

# ---- TOTAL FEATURES MODEL EXPECTS (19) ----
TOTAL_FEATURES = model.n_features_in_

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Base input (5 features)
        base_values = [data[f] for f in BASE_FEATURES]

        # Fill remaining engineered features with 0 (safe demo default)
        remaining = TOTAL_FEATURES - len(base_values)
        full_input = base_values + [0.0] * remaining

        input_array = np.array([full_input])

        # Prediction
        prob = model.predict_proba(input_array)[0][1]

        # SHAP explanation
        shap_values = explainer(input_array)
        shap_contrib = shap_values.values[0][:len(BASE_FEATURES)]

        explanation = dict(zip(BASE_FEATURES, shap_contrib.tolist()))

        return jsonify({
            "failure_probability": round(float(prob), 3),
            "shap_explanation": explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
