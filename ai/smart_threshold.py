import json
import pandas as pd
from datetime import datetime, timedelta

def calculate_dynamic_threshold():
    """Calculate adaptive threshold based on recent deployment success"""
    try:
        # Load recent deployment data (last 30 days)
        df = pd.read_csv('ai/training_data.csv')
        df['timestamp'] = pd.to_datetime(df.get('timestamp', datetime.now()))
        
        recent_data = df[df['timestamp'] > datetime.now() - timedelta(days=30)]
        
        if len(recent_data) < 10:
            return 0.524  # Default threshold
            
        # Calculate success rate
        success_rate = recent_data['proceed'].mean()
        
        # Adjust threshold based on recent performance
        if success_rate < 0.7:  # Low success rate, be more conservative
            return 0.6
        elif success_rate > 0.9:  # High success rate, be more aggressive
            return 0.4
        else:
            return 0.524  # Default
            
    except Exception as e:
        print(f"Error calculating dynamic threshold: {e}")
        return 0.524

def get_deployment_trend():
    """Analyze deployment trends and patterns"""
    try:
        df = pd.read_csv('ai/training_data.csv')
        
        # Calculate rolling success rate
        df['rolling_success'] = df['proceed'].rolling(window=10, min_periods=5).mean()
        
        # Detect trend (improving/degrading)
        recent_trend = df['rolling_success'].tail(5).mean()
        older_trend = df['rolling_success'].tail(15).head(10).mean()
        
        trend = "improving" if recent_trend > older_trend else "degrading"
        
        return {
            'trend': trend,
            'recent_success_rate': round(recent_trend, 3),
            'confidence': abs(recent_trend - older_trend)
        }
    except:
        return {'trend': 'unknown', 'recent_success_rate': 0.5, 'confidence': 0}