import json
from datetime import datetime, timedelta

class ContextualIntelligence:
    @staticmethod
    def get_deployment_context():
        """Gather contextual information for smarter decisions"""
        now = datetime.now()
        
        context = {
            'time_context': {
                'is_business_hours': 9 <= now.hour <= 17,
                'is_weekend': now.weekday() >= 5,
                'is_friday_afternoon': now.weekday() == 4 and now.hour >= 15,
                'is_holiday_season': now.month == 12,  # December deployments
            },
            'deployment_timing': {
                'hour': now.hour,
                'day_of_week': now.weekday(),
                'is_end_of_month': now.day >= 25,
                'quarter_end': now.month in [3, 6, 9, 12] and now.day >= 25
            }
        }
        
        return context
    
    @staticmethod
    def apply_contextual_rules(base_decision, signals, context):
        """Apply contextual intelligence to modify decisions"""
        modified_decision = base_decision.copy()
        contextual_factors = []
        
        # Friday afternoon rule - be more conservative
        if context['time_context']['is_friday_afternoon']:
            if base_decision.get('proceed', False):
                # Increase threshold for Friday afternoon deployments
                if base_decision.get('prob', 0) < 0.7:
                    modified_decision['proceed'] = False
                    modified_decision['reasons'].append('friday_afternoon_caution')
                    contextual_factors.append('Friday afternoon deployment blocked for safety')
        
        # Weekend emergency deployment
        if context['time_context']['is_weekend']:
            contextual_factors.append('Weekend deployment detected - ensure emergency approval')
        
        # High-risk + business hours = extra caution
        if (context['time_context']['is_business_hours'] and 
            signals.get('changed_files', 0) > 15):
            contextual_factors.append('Large change during business hours - consider impact')
        
        # Holiday season caution
        if context['time_context']['is_holiday_season']:
            contextual_factors.append('Holiday season deployment - extra monitoring recommended')
        
        # Quarter-end deployment
        if context['deployment_timing']['quarter_end']:
            contextual_factors.append('Quarter-end deployment - financial system impact possible')
        
        modified_decision['contextual_factors'] = contextual_factors
        modified_decision['deployment_context'] = context
        
        return modified_decision
    
    @staticmethod
    def recommend_deployment_window(signals):
        """Recommend optimal deployment timing"""
        now = datetime.now()
        
        # Calculate risk-adjusted time windows
        recommendations = []
        
        if now.weekday() == 4 and now.hour >= 15:  # Friday afternoon
            recommendations.append("Consider delaying to Monday morning")
        
        if signals.get('changed_files', 0) > 20:
            recommendations.append("Large change detected - deploy during low-traffic hours")
        
        if signals.get('failures', 0) > 0:
            recommendations.append("Test failures present - do not deploy until fixed")
        
        if now.weekday() >= 5:  # Weekend
            recommendations.append("Weekend deployment - ensure on-call coverage")
        
        return recommendations