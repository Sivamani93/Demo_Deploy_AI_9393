import numpy as np
from sklearn.ensemble import IsolationForest
import json

class AnomalyDetector:
    def __init__(self):
        self.detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        
    def train(self, historical_data):
        """Train anomaly detector on historical deployment signals"""
        if len(historical_data) > 10:
            features = ['failures', 'lint_warnings', 'changed_files', 'apk_size_mb',
                       'apk_size_delta_ratio', 'coverage_pct', 'build_duration_s']
            X = [[d.get(f, 0) for f in features] for d in historical_data]
            self.detector.fit(X)
            self.is_trained = True
            
    def detect_anomaly(self, signals):
        """Detect if current signals are anomalous"""
        if not self.is_trained:
            return {'is_anomaly': False, 'anomaly_score': 0, 'reason': 'not_trained'}
            
        features = ['failures', 'lint_warnings', 'changed_files', 'apk_size_mb',
                   'apk_size_delta_ratio', 'coverage_pct', 'build_duration_s']
        X = [[signals.get(f, 0) for f in features]]
        
        anomaly_score = self.detector.decision_function(X)[0]
        is_anomaly = self.detector.predict(X)[0] == -1
        
        # Identify which features are most unusual
        unusual_features = []
        for feature in features:
            value = signals.get(feature, 0)
            if feature == 'failures' and value > 5:
                unusual_features.append(f"High failures: {value}")
            elif feature == 'lint_warnings' and value > 50:
                unusual_features.append(f"Excessive lint warnings: {value}")
            elif feature == 'apk_size_delta_ratio' and abs(value) > 0.5:
                unusual_features.append(f"Large APK size change: {value}")
                
        return {
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': round(float(anomaly_score), 3),
            'unusual_features': unusual_features,
            'reason': 'anomaly_detected' if is_anomaly else 'normal'
        }

def load_anomaly_detector():
    """Load and train anomaly detector from historical data"""
    try:
        import pandas as pd
        df = pd.read_csv('ai/training_data.csv')
        historical_signals = df.to_dict('records')
        
        detector = AnomalyDetector()
        detector.train(historical_signals)
        return detector
    except:
        return AnomalyDetector()  # Return untrained detector