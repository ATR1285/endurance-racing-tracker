"""
Machine Learning models for endurance racing predictions.
Includes lap time prediction, anomaly detection, and strategy optimization.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LapTimePredictor:
    """Predicts next lap time using Random Forest"""
    
    def __init__(self, model_path: str = "models/lap_time_model.pkl"):
        self.model = None
        self.model_path = Path(model_path)
        self.feature_names = [
            'last_lap_time', 'avg_last_5_laps', 'std_last_5_laps',
            'best_lap_time', 'tire_age', 'laps_completed',
            'sector1_avg', 'sector2_avg', 'sector3_avg',
            'hour_of_day', 'is_night'
        ]
    
    def train(self, training_data: pd.DataFrame) -> Dict:
        """
        Train the lap time prediction model.
        
        Args:
            training_data: DataFrame with features and target 'next_lap_time'
        
        Returns:
            Training metrics
        """
        if len(training_data) < 100:
            logger.warning("Insufficient training data (< 100 samples)")
            return {}
        
        # Prepare features and target
        X = training_data[self.feature_names]
        y = training_data['next_lap_time']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        logger.info("Training lap time prediction model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model trained - MAE: {mae:.3f}s, R²: {r2:.3f}")
        
        # Save model
        self.save_model()
        
        return {
            'mae': mae,
            'r2': r2,
            'samples': len(training_data)
        }
    
    def predict(self, features: Dict) -> Tuple[float, float]:
        """
        Predict next lap time.
        
        Args:
            features: Dict of feature values
        
        Returns:
            (predicted_lap_time, confidence)
        """
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            return 0.0, 0.0
        
        # Prepare feature vector
        X = np.array([[features.get(f, 0) for f in self.feature_names]])
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        # Estimate confidence based on feature importance and variance
        # Use standard deviation of tree predictions as uncertainty measure
        tree_predictions = np.array([tree.predict(X)[0] for tree in self.model.estimators_])
        std = np.std(tree_predictions)
        
        # Convert std to confidence (0-1)
        confidence = max(0.0, min(1.0, 1.0 - (std / prediction)))
        
        return prediction, confidence
    
    def save_model(self):
        """Save trained model to disk"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
        else:
            logger.warning(f"No model found at {self.model_path}")


class AnomalyDetector:
    """Detects anomalies in lap times using Isolation Forest"""
    
    def __init__(self, model_path: str = "models/anomaly_model.pkl"):
        self.model = None
        self.model_path = Path(model_path)
        self.contamination = 0.05  # Expected proportion of anomalies
    
    def train(self, training_data: pd.DataFrame) -> Dict:
        """
        Train anomaly detection model.
        
        Args:
            training_data: DataFrame with lap time features
        
        Returns:
            Training metrics
        """
        if len(training_data) < 50:
            logger.warning("Insufficient training data for anomaly detection")
            return {}
        
        # Features for anomaly detection
        features = ['lap_time', 'sector1_time', 'sector2_time', 'sector3_time']
        X = training_data[features].fillna(0)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        
        logger.info("Training anomaly detection model...")
        self.model.fit(X)
        
        # Save model
        self.save_model()
        
        return {
            'samples': len(training_data),
            'contamination': self.contamination
        }
    
    def detect(self, lap_data: Dict) -> Tuple[bool, float, str]:
        """
        Detect if a lap is anomalous.
        
        Args:
            lap_data: Dict with lap time and sector times
        
        Returns:
            (is_anomaly, severity, description)
        """
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            return False, 0.0, ""
        
        # Prepare features
        X = np.array([[
            lap_data.get('lap_time', 0),
            lap_data.get('sector1_time', 0),
            lap_data.get('sector2_time', 0),
            lap_data.get('sector3_time', 0)
        ]])
        
        # Predict (-1 = anomaly, 1 = normal)
        prediction = self.model.predict(X)[0]
        
        # Get anomaly score (lower = more anomalous)
        score = self.model.score_samples(X)[0]
        severity = max(0.0, min(1.0, -score))  # Normalize to 0-1
        
        is_anomaly = prediction == -1
        
        # Determine anomaly type
        description = ""
        if is_anomaly:
            lap_time = lap_data.get('lap_time', 0)
            sector_times = [
                lap_data.get('sector1_time', 0),
                lap_data.get('sector2_time', 0),
                lap_data.get('sector3_time', 0)
            ]
            
            # Check which sector is problematic
            if max(sector_times) > sum(sector_times) * 0.5:
                slow_sector = sector_times.index(max(sector_times)) + 1
                description = f"Slow sector {slow_sector} - possible incident or traffic"
            elif lap_time > 200:
                description = "Extremely slow lap - possible pit stop or mechanical issue"
            else:
                description = "Unusual lap time pattern detected"
        
        return is_anomaly, severity, description
    
    def save_model(self):
        """Save model to disk"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Anomaly model saved to {self.model_path}")
    
    def load_model(self):
        """Load model from disk"""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            logger.info(f"Anomaly model loaded from {self.model_path}")
        else:
            logger.warning(f"No anomaly model found at {self.model_path}")


class StrategyEngine:
    """Advanced pit strategy recommendations"""
    
    def __init__(self):
        self.fuel_consumption_rates = {}  # car_id -> liters/lap
        self.tire_degradation = {}  # car_id -> degradation curve
        self.avg_pit_duration = 60.0  # seconds
    
    def set_fuel_rate(self, car_id: int, rate: float):
        """Set fuel consumption rate for a car"""
        self.fuel_consumption_rates[car_id] = rate
    
    def set_tire_degradation(self, car_id: int, degradation: List[Tuple[int, float]]):
        """Set tire degradation curve for a car"""
        self.tire_degradation[car_id] = degradation
    
    def recommend_pit_stop(
        self,
        car_id: int,
        current_lap: int,
        fuel_remaining: float,
        tire_age: int,
        gap_to_ahead: float,
        gap_to_behind: float,
        race_laps_remaining: int
    ) -> Dict:
        """
        Generate pit stop recommendation.
        
        Args:
            car_id: Car identifier
            current_lap: Current lap number
            fuel_remaining: Fuel remaining (liters)
            tire_age: Laps on current tires
            gap_to_ahead: Gap to car ahead (seconds)
            gap_to_behind: Gap to car behind (seconds)
            race_laps_remaining: Laps until race end
        
        Returns:
            Strategy recommendation dict
        """
        fuel_rate = self.fuel_consumption_rates.get(car_id, 2.5)
        
        # Calculate fuel window
        laps_on_fuel = int(fuel_remaining / fuel_rate)
        fuel_critical_lap = current_lap + laps_on_fuel - 1
        
        # Calculate tire degradation penalty
        tire_penalty = 0.0
        if car_id in self.tire_degradation:
            curve = self.tire_degradation[car_id]
            for age, delta in curve:
                if age >= tire_age:
                    tire_penalty = delta
                    break
        
        # Determine if tire change is needed
        tire_change_needed = tire_age > 30 or tire_penalty > 1.5
        
        # Calculate optimal pit lap
        # Factors: fuel, tire deg, traffic, race remaining
        
        # Don't pit if less than 10 laps remaining and fuel is OK
        if race_laps_remaining < 10 and laps_on_fuel >= race_laps_remaining:
            return {
                'recommended_pit_lap': None,
                'laps_until_pit': None,
                'reasoning': "No pit stop needed - sufficient fuel to finish",
                'fuel_remaining_laps': laps_on_fuel,
                'tire_degradation': tire_penalty,
                'optimal_tire_change': False,
                'optimal_fuel_load': 0,
                'estimated_pit_duration': 0
            }
        
        # Pit before running out of fuel (2 lap buffer)
        max_stint = min(laps_on_fuel - 2, 35)  # Max 35 lap stint
        
        # Adjust for tire degradation
        if tire_change_needed and max_stint > 10:
            max_stint = min(max_stint, 30)
        
        # Adjust for traffic (avoid pitting when close to cars)
        traffic_penalty = 0
        if gap_to_ahead < 5.0 or gap_to_behind < 5.0:
            traffic_penalty = 2  # Wait 2 more laps if in traffic
        
        optimal_pit_lap = current_lap + max_stint + traffic_penalty
        
        # Calculate fuel load needed
        laps_after_pit = race_laps_remaining - (optimal_pit_lap - current_lap)
        fuel_needed = min(laps_after_pit * fuel_rate * 1.1, 90)  # 10% buffer, max 90L
        
        # Estimate pit duration
        pit_duration = self.avg_pit_duration
        if tire_change_needed:
            pit_duration += 10  # Extra time for tire change
        
        reasoning = f"Pit on lap {optimal_pit_lap} for "
        if tire_change_needed:
            reasoning += "tires and fuel"
        else:
            reasoning += "fuel only"
        
        if traffic_penalty > 0:
            reasoning += " (delayed for traffic)"
        
        return {
            'recommended_pit_lap': optimal_pit_lap,
            'laps_until_pit': optimal_pit_lap - current_lap,
            'reasoning': reasoning,
            'fuel_remaining_laps': laps_on_fuel,
            'tire_degradation': tire_penalty,
            'optimal_tire_change': tire_change_needed,
            'optimal_fuel_load': fuel_needed,
            'estimated_pit_duration': pit_duration
        }
