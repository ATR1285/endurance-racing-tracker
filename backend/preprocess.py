"""
Data preprocessing and feature engineering for endurance racing.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RaceDataPreprocessor:
    """Preprocesses race data for ML models and analysis"""
    
    def __init__(self):
        self.class_avg_lap_times = {}  # Track average lap times per class
        self.fuel_consumption_rates = {}  # liters per lap per car
        self.tire_degradation_curves = {}  # lap time delta vs stint length
    
    def normalize_lap_times(self, laps_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize lap times across different classes.
        Remove outliers (pit laps, slow laps due to incidents).
        """
        if laps_df.empty:
            return laps_df
        
        # Remove pit laps and outlaps
        clean_laps = laps_df[~laps_df['is_pit_lap'] & ~laps_df['is_outlap']].copy()
        
        # Calculate class averages
        for car_class in clean_laps['car_class'].unique():
            class_laps = clean_laps[clean_laps['car_class'] == car_class]['lap_time']
            if len(class_laps) > 0:
                self.class_avg_lap_times[car_class] = class_laps.median()
        
        # Remove statistical outliers (> 3 std deviations)
        for car_class in clean_laps['car_class'].unique():
            class_mask = clean_laps['car_class'] == car_class
            class_laps = clean_laps[class_mask]['lap_time']
            
            if len(class_laps) > 10:
                mean = class_laps.mean()
                std = class_laps.std()
                outlier_mask = (class_laps > mean + 3*std) | (class_laps < mean - 3*std)
                clean_laps.loc[class_mask & outlier_mask, 'is_outlier'] = True
        
        return clean_laps
    
    def calculate_gaps(self, positions_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate gaps to leader (overall and in-class)"""
        if positions_df.empty:
            return positions_df
        
        result = positions_df.copy()
        
        # Overall gap to leader
        leader_laps = result[result['position'] == 1]['laps_completed'].iloc[0]
        result['gap_to_leader_laps'] = leader_laps - result['laps_completed']
        
        # In-class gap to leader
        for car_class in result['car_class'].unique():
            class_mask = result['car_class'] == car_class
            class_leader_laps = result[class_mask & (result['position_in_class'] == 1)]['laps_completed']
            
            if len(class_leader_laps) > 0:
                class_leader_laps = class_leader_laps.iloc[0]
                result.loc[class_mask, 'gap_to_class_leader_laps'] = class_leader_laps - result.loc[class_mask, 'laps_completed']
        
        return result
    
    def track_driver_stints(self, stints_df: pd.DataFrame, laps_df: pd.DataFrame) -> pd.DataFrame:
        """
        Track driver stint performance and estimate fatigue effects.
        """
        if stints_df.empty:
            return stints_df
        
        result = stints_df.copy()
        
        for idx, stint in result.iterrows():
            if pd.isna(stint['end_lap']):
                # Current stint
                stint_laps = laps_df[
                    (laps_df['car_id'] == stint['car_id']) &
                    (laps_df['lap_number'] >= stint['start_lap'])
                ]
            else:
                stint_laps = laps_df[
                    (laps_df['car_id'] == stint['car_id']) &
                    (laps_df['lap_number'] >= stint['start_lap']) &
                    (laps_df['lap_number'] <= stint['end_lap'])
                ]
            
            if len(stint_laps) > 0:
                result.loc[idx, 'stint_laps'] = len(stint_laps)
                result.loc[idx, 'avg_lap_time'] = stint_laps['lap_time'].mean()
                result.loc[idx, 'best_lap_time'] = stint_laps['lap_time'].min()
                
                # Estimate fatigue (lap time increase over stint)
                if len(stint_laps) > 5:
                    first_5 = stint_laps.head(5)['lap_time'].mean()
                    last_5 = stint_laps.tail(5)['lap_time'].mean()
                    result.loc[idx, 'fatigue_delta'] = last_5 - first_5
        
        return result
    
    def calculate_tire_degradation(self, laps_df: pd.DataFrame) -> Dict[int, List[float]]:
        """
        Calculate tire degradation curves for each car.
        Returns dict of car_id -> list of lap time deltas vs stint length.
        """
        degradation = {}
        
        for car_id in laps_df['car_id'].unique():
            car_laps = laps_df[laps_df['car_id'] == car_id].sort_values('lap_number')
            
            if len(car_laps) < 10:
                continue
            
            # Group by tire age
            tire_age_groups = car_laps.groupby('tire_age')['lap_time'].mean()
            
            if len(tire_age_groups) > 3:
                # Calculate degradation rate (seconds per lap on tires)
                baseline = tire_age_groups.iloc[0]
                deltas = [(age, time - baseline) for age, time in tire_age_groups.items()]
                degradation[car_id] = deltas
                
                # Store for later use
                self.tire_degradation_curves[car_id] = deltas
        
        return degradation
    
    def estimate_fuel_consumption(self, laps_df: pd.DataFrame, stint_length: int = 30) -> Dict[int, float]:
        """
        Estimate fuel consumption rate (liters per lap) for each car.
        Based on typical stint lengths and fuel tank capacity.
        """
        consumption = {}
        
        # Typical fuel tank: 75-90 liters for prototypes, 100-120 for GT
        # Typical stint: 25-35 laps
        
        for car_id in laps_df['car_id'].unique():
            car_laps = laps_df[laps_df['car_id'] == car_id]
            car_class = car_laps['car_class'].iloc[0] if len(car_laps) > 0 else 'Unknown'
            
            # Estimate based on class
            if 'Hypercar' in car_class or 'DPi' in car_class or 'LMP' in car_class:
                tank_capacity = 80  # liters
            else:
                tank_capacity = 110  # GT cars
            
            # Assume typical stint length
            consumption_rate = tank_capacity / stint_length
            consumption[car_id] = consumption_rate
            self.fuel_consumption_rates[car_id] = consumption_rate
        
        return consumption
    
    def detect_pit_stops(self, laps_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect pit stops from lap data.
        Categorize as fuel only, tires, or driver change based on duration.
        """
        pit_stops = []
        
        for car_id in laps_df['car_id'].unique():
            car_laps = laps_df[laps_df['car_id'] == car_id].sort_values('lap_number')
            
            # Find pit laps (marked or significantly slower)
            pit_laps = car_laps[car_laps['is_pit_lap']]
            
            for idx, pit_lap in pit_laps.iterrows():
                lap_time = pit_lap['lap_time']
                avg_lap = car_laps[~car_laps['is_pit_lap']]['lap_time'].median()
                
                if pd.isna(avg_lap):
                    continue
                
                pit_duration = lap_time - avg_lap
                
                # Categorize based on duration
                if pit_duration < 30:
                    stop_type = 'fuel_only'
                elif pit_duration < 60:
                    stop_type = 'tires'
                else:
                    stop_type = 'driver_change'
                
                pit_stops.append({
                    'car_id': car_id,
                    'lap_number': pit_lap['lap_number'],
                    'duration': pit_duration,
                    'stop_type': stop_type,
                    'timestamp': pit_lap['timestamp']
                })
        
        return pd.DataFrame(pit_stops)
    
    def prepare_ml_features(self, laps_df: pd.DataFrame, current_lap: int, car_id: int) -> Dict:
        """
        Prepare features for ML prediction models.
        Returns feature dict for a specific car at current lap.
        """
        car_laps = laps_df[
            (laps_df['car_id'] == car_id) &
            (laps_df['lap_number'] <= current_lap)
        ].sort_values('lap_number')
        
        if len(car_laps) < 3:
            return {}
        
        # Recent lap times
        recent_5 = car_laps.tail(5)['lap_time'].tolist()
        
        features = {
            'last_lap_time': car_laps.iloc[-1]['lap_time'],
            'avg_last_5_laps': np.mean(recent_5),
            'std_last_5_laps': np.std(recent_5),
            'best_lap_time': car_laps['lap_time'].min(),
            'tire_age': car_laps.iloc[-1]['tire_age'] if 'tire_age' in car_laps.columns else 0,
            'laps_completed': current_lap,
            'sector1_avg': car_laps['sector1_time'].mean() if 'sector1_time' in car_laps.columns else 0,
            'sector2_avg': car_laps['sector2_time'].mean() if 'sector2_time' in car_laps.columns else 0,
            'sector3_avg': car_laps['sector3_time'].mean() if 'sector3_time' in car_laps.columns else 0,
        }
        
        # Add time of day (racing at night vs day affects performance)
        if 'timestamp' in car_laps.columns:
            current_time = car_laps.iloc[-1]['timestamp']
            if isinstance(current_time, datetime):
                features['hour_of_day'] = current_time.hour
                features['is_night'] = 1 if current_time.hour < 6 or current_time.hour > 20 else 0
        
        return features
    
    def calculate_pit_window(self, car_id: int, current_lap: int, fuel_remaining: float, tire_age: int) -> Dict:
        """
        Calculate optimal pit window based on fuel, tires, and strategy.
        """
        fuel_rate = self.fuel_consumption_rates.get(car_id, 2.5)  # default 2.5 L/lap
        
        # Laps remaining on fuel
        laps_on_fuel = fuel_remaining / fuel_rate
        
        # Tire degradation penalty
        tire_penalty = 0
        if car_id in self.tire_degradation_curves:
            curve = self.tire_degradation_curves[car_id]
            # Find penalty at current tire age
            for age, delta in curve:
                if age >= tire_age:
                    tire_penalty = delta
                    break
        
        # Optimal pit lap (before running out of fuel, when tire penalty is high)
        optimal_pit_lap = current_lap + min(int(laps_on_fuel) - 2, 35)  # Max 35 lap stint
        
        return {
            'optimal_pit_lap': optimal_pit_lap,
            'laps_until_pit': optimal_pit_lap - current_lap,
            'fuel_remaining_laps': laps_on_fuel,
            'tire_penalty': tire_penalty,
            'recommended_tire_change': tire_age > 25 or tire_penalty > 1.0
        }
