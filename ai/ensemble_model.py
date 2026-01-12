import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import cross_val_score
import json

class EnsemblePredictor:
    def __init__(self):
        self.models = {
            'logistic': LogisticRegression(max_iter=1000, class_weight='balanced'),
            'random_forest': RandomForestClassifier(n_estimators=100, class_weight='balanced'),
            'gradient_boost': GradientBoostingClassifier(n_estimators=100)
        }
        self.calibrated_models = {}
        self.weights = {}
        
    def train(self, X, y):
        """Train ensemble of models"""
        for name, model in self.models.items():
            # Train with calibration
            calibrated = CalibratedClassifierCV(model, cv=3, method='sigmoid')
            calibrated.fit(X, y)
            self.calibrated_models[name] = calibrated
            
            # Calculate model weight based on cross-validation score
            try:
                cv_score = cross_val_score(model, X, y, cv=3, scoring='roc_auc').mean()
                self.weights[name] = max(cv_score, 0.5)  # Minimum weight 0.5
            except:
                self.weights[name] = 0.5
                
        # Normalize weights
        total_weight = sum(self.weights.values())
        self.weights = {k: v/total_weight for k, v in self.weights.items()}
        
    def predict_ensemble(self, X):
        """Make ensemble prediction with confidence intervals"""
        predictions = {}
        probabilities = {}
        
        for name, model in self.calibrated_models.items():
            pred_proba = model.predict_proba(X)[0]
            predictions[name] = {
                'probability': float(pred_proba[1]),
                'weight': self.weights[name]
            }
            probabilities[name] = pred_proba[1]
            
        # Weighted ensemble prediction
        ensemble_prob = sum(prob * self.weights[name] 
                          for name, prob in probabilities.items())
        
        # Calculate prediction variance (uncertainty)
        prob_variance = np.var(list(probabilities.values()))
        
        # Calculate consensus (how much models agree)
        consensus = 1 - prob_variance  # High variance = low consensus
        
        return {
            'ensemble_probability': round(float(ensemble_prob), 3),
            'individual_predictions': predictions,
            'consensus': round(float(consensus), 3),
            'uncertainty': round(float(prob_variance), 3)
        }