import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime, timedelta
from typing import List, Dict

def sigmoid(t, k, t0):
    """
    Sigmoid function for spoilage curve fitting.
    f(t) = 1 / (1 + exp(-k*(t - t0)))
    """
    return 1 / (1 + np.exp(-k * (t - t0)))

def predict_spoilage_local(readings: List[Dict], food_category: str) -> Dict:
    """
    Local prediction engine with two layers:
    1. Rule-based (fallback/low data)
    2. Sigmoid curve fitting (>= 3 readings)
    """
    # Midpoint shelf-life in hours
    SHELF_LIFE_MAP = {
        "raw_meat": 60.0,
        "dairy": 144.0,
        "leafy": 96.0,
        "cooked": 84.0
    }
    base_shelf_life = SHELF_LIFE_MAP.get(food_category, 72.0)

    # Layer 1 logic helper
    def get_rule_based_prediction(score: float):
        hours_remaining = base_shelf_life * (1.0 - score)
        return {
            "predicted_spoil_by": datetime.now() + timedelta(hours=hours_remaining),
            "hours_remaining": hours_remaining,
            "confidence": 0.6,
            "method": "rule_based"
        }

    if not readings:
        return get_rule_based_prediction(0.0)

    # Note: ingest.py passes readings ordered by timestamp DESC
    latest_reading = readings[0]
    current_score = latest_reading["spoilage_score"]

    if len(readings) < 3:
        return get_rule_based_prediction(current_score)

    # Layer 2: Curve fitting
    try:
        # Prepare data (reverse to ASC order for time calculations)
        history = sorted(readings, key=lambda x: x["timestamp"])
        first_ts = datetime.fromisoformat(history[0]["timestamp"])
        
        t_data = []
        y_data = []
        for r in history:
            ts = datetime.fromisoformat(r["timestamp"])
            elapsed_hours = (ts - first_ts).total_seconds() / 3600.0
            t_data.append(elapsed_hours)
            y_data.append(r["spoilage_score"])
        
        t_data = np.array(t_data)
        y_data = np.array(y_data)

        # Fit sigmoid curve
        # Initial guess: k=0.1, t0=base_shelf_life/2
        popt, _ = curve_fit(sigmoid, t_data, y_data, p0=[0.1, base_shelf_life/2], maxfev=2000)
        k, t0 = popt

        # Solve for t when f(t) = 0.75 (spoilage threshold)
        # t = t0 - (ln(1/0.75 - 1) / k)
        t_spoil = t0 - (np.log(1/0.75 - 1) / k)
        
        predicted_dt = first_ts + timedelta(hours=t_spoil)
        hours_remaining = (predicted_dt - datetime.now()).total_seconds() / 3600.0

        return {
            "predicted_spoil_by": predicted_dt,
            "hours_remaining": max(0, hours_remaining),
            "confidence": 0.85,
            "method": "curve_fit"
        }

    except Exception as e:
        # Fallback to Layer 1 if fit fails or converges poorly
        print(f"Predictor Error (Curve Fit failed): {str(e)}")
        return get_rule_based_prediction(current_score)
