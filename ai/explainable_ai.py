try:
    import shap
    import numpy as np
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

class ExplainableAI:
    def __init__(self, model, scaler, feature_names):
        self.model = model
        self.scaler = scaler
        self.feature_names = feature_names
        self.explainer = None
        
        if SHAP_AVAILABLE:
            try:
                # Create SHAP explainer
                self.explainer = shap.Explainer(self.model.predict_proba, feature_names=feature_names)
            except:
                self.explainer = None
    
    def explain_prediction(self, signals):
        """Generate detailed explanations for ML predictions"""
        feature_values = [signals.get(f, 0) for f in self.feature_names]
        scaled_features = self.scaler.transform([feature_values])
        
        explanation = {
            'feature_contributions': {},
            'top_positive_factors': [],
            'top_negative_factors': [],
            'explanation_confidence': 0.0
        }
        
        if SHAP_AVAILABLE and self.explainer:
            try:
                # Calculate SHAP values
                shap_values = self.explainer(scaled_features)
                
                # Get SHAP values for the positive class (proceed)
                proceed_shap = shap_values[0][:, 1] if len(shap_values[0].shape) > 1 else shap_values[0]
                
                # Create feature contributions
                for i, (feature, value, contribution) in enumerate(
                    zip(self.feature_names, feature_values, proceed_shap)):
                    explanation['feature_contributions'][feature] = {
                        'value': value,
                        'contribution': float(contribution),
                        'impact': 'positive' if contribution > 0 else 'negative'
                    }
                
                # Sort by contribution magnitude
                sorted_contributions = sorted(
                    explanation['feature_contributions'].items(),
                    key=lambda x: abs(x[1]['contribution']),
                    reverse=True
                )
                
                # Top positive and negative factors
                for feature, contrib in sorted_contributions[:3]:
                    if contrib['contribution'] > 0:
                        explanation['top_positive_factors'].append(
                            f"{feature}={contrib['value']} (+{contrib['contribution']:.3f})"
                        )
                    else:
                        explanation['top_negative_factors'].append(
                            f"{feature}={contrib['value']} ({contrib['contribution']:.3f})"
                        )
                
                explanation['explanation_confidence'] = 0.9
                
            except Exception as e:
                explanation['error'] = f"SHAP explanation failed: {str(e)}"
                explanation['explanation_confidence'] = 0.0
        else:
            # Fallback explanation without SHAP
            explanation = self._fallback_explanation(signals, feature_values)
            
        return explanation
    
    def _fallback_explanation(self, signals, feature_values):
        """Fallback explanation when SHAP is not available"""
        explanation = {
            'feature_contributions': {},
            'top_positive_factors': [],
            'top_negative_factors': [],
            'explanation_confidence': 0.6
        }
        
        # Simple rule-based explanations
        risk_features = ['failures', 'secrets_found', 'lint_warnings']
        quality_features = ['coverage_pct']
        
        for feature, value in zip(self.feature_names, feature_values):
            if feature in risk_features and value > 0:
                explanation['top_negative_factors'].append(f"{feature}: {value}")
            elif feature in quality_features and value > 80:
                explanation['top_positive_factors'].append(f"{feature}: {value}%")
                
        return explanation
    
    def generate_natural_language_explanation(self, explanation, decision):
        """Generate human-readable explanation"""
        if decision.get('proceed', False):
            base_text = "✅ PROCEED recommendation because: "
        else:
            base_text = "❌ BLOCK recommendation because: "
            
        factors = []
        
        # Add top factors
        if explanation['top_negative_factors']:
            factors.append(f"Risk factors: {', '.join(explanation['top_negative_factors'][:2])}")
            
        if explanation['top_positive_factors']:
            factors.append(f"Quality indicators: {', '.join(explanation['top_positive_factors'][:2])}")
            
        if not factors:
            factors.append("balanced risk assessment")
            
        return base_text + "; ".join(factors)