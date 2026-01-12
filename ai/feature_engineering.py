import numpy as np
from datetime import datetime, timedelta

class FeatureEngineer:
    @staticmethod
    def engineer_features(signals):
        """Create intelligent derived features from raw signals"""
        enhanced = signals.copy()
        
        # Risk ratios and combinations
        enhanced['risk_ratio'] = (
            signals.get('failures', 0) * 3 + 
            signals.get('lint_warnings', 0) * 0.1 + 
            signals.get('secrets_found', 0) * 5
        )
        
        # Quality score (0-100)
        coverage = signals.get('coverage_pct', 0)
        lint_warnings = signals.get('lint_warnings', 0)
        enhanced['quality_score'] = max(0, min(100, 
            coverage - (lint_warnings * 2) - (signals.get('failures', 0) * 10)
        ))
        
        # Change velocity (how much is changing)
        enhanced['change_velocity'] = (
            signals.get('changed_files', 0) * 
            (1 + signals.get('apk_size_delta_ratio', 0))
        )
        
        # Complexity indicator
        enhanced['complexity_indicator'] = (
            signals.get('changed_files', 0) > 10 and
            signals.get('apk_size_delta_ratio', 0) > 0.2 and
            signals.get('build_duration_s', 0) > 180
        )
        
        # Time-based features
        now = datetime.now()
        enhanced['hour_of_day'] = now.hour
        enhanced['day_of_week'] = now.weekday()
        enhanced['is_friday_deployment'] = now.weekday() == 4  # Friday deployments are riskier
        
        # Feature interactions
        enhanced['lint_per_file'] = (
            signals.get('lint_warnings', 0) / max(1, signals.get('changed_files', 1))
        )
        
        enhanced['test_coverage_vs_changes'] = (
            signals.get('coverage_pct', 0) - 
            (signals.get('changed_files', 0) * 2)  # More changes should need more coverage
        )
        
        return enhanced
    
    @staticmethod
    def create_risk_categories(signals):
        """Categorize deployment into risk levels"""
        enhanced = FeatureEngineer.engineer_features(signals)
        
        # Calculate risk level
        risk_score = 0
        
        if enhanced.get('failures', 0) > 0:
            risk_score += 50
        if enhanced.get('secrets_found', 0) > 0:
            risk_score += 40
        if enhanced.get('quality_score', 100) < 70:
            risk_score += 20
        if enhanced.get('change_velocity', 0) > 20:
            risk_score += 15
        if enhanced.get('is_friday_deployment', False):
            risk_score += 10
            
        # Risk categories
        if risk_score >= 70:
            risk_level = 'HIGH'
        elif risk_score >= 40:
            risk_level = 'MEDIUM'
        elif risk_score >= 20:
            risk_level = 'LOW'
        else:
            risk_level = 'MINIMAL'
            
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'enhanced_features': enhanced
        }