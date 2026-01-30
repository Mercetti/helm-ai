"""
Traffic Pattern Generator for Helm AI
Simulates realistic traffic patterns based on real-world usage analytics
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class TrafficPatternGenerator:
    """
    Generates realistic traffic patterns for load testing
    Based on typical SaaS application usage patterns
    """
    
    def __init__(self):
        self.base_hourly_pattern = self._generate_hourly_pattern()
        self.base_weekly_pattern = self._generate_weekly_pattern()
        self.base_monthly_pattern = self._generate_monthly_pattern()
        
    def _generate_hourly_pattern(self) -> List[float]:
        """Generate hourly traffic pattern (24-hour cycle)"""
        # Typical SaaS hourly pattern
        hourly_pattern = [
            0.1,  # 12am-1am
            0.05, # 1am-2am
            0.05, # 2am-3am
            0.05, # 3am-4am
            0.05, # 4am-5am
            0.1,  # 5am-6am
            0.3,  # 6am-7am
            0.6,  # 7am-8am
            0.8,  # 8am-9am
            1.0,  # 9am-10am (peak)
            0.9,  # 10am-11am
            0.8,  # 11am-12pm
            0.7,  # 12pm-1pm (lunch dip)
            0.6,  # 1pm-2pm
            0.8,  # 2pm-3pm
            0.9,  # 3pm-4pm (peak)
            0.8,  # 4pm-5pm
            0.6,  # 5pm-6pm
            0.4,  # 6pm-7pm
            0.3,  # 7pm-8pm
            0.2,  # 8pm-9pm
            0.15, # 9pm-10pm
            0.1,  # 10pm-11pm
            0.05  # 11pm-12am
        ]
        return hourly_pattern
    
    def _generate_weekly_pattern(self) -> List[float]:
        """Generate weekly traffic pattern"""
        # Monday = 0, Sunday = 6
        weekly_pattern = [
            1.0,  # Monday
            0.95, # Tuesday
            0.9,  # Wednesday
            0.85, # Thursday
            0.8,  # Friday
            0.4,  # Saturday
            0.3   # Sunday
        ]
        return weekly_pattern
    
    def _generate_monthly_pattern(self) -> List[float]:
        """Generate monthly traffic pattern"""
        # Days 1-31
        monthly_pattern = []
        for day in range(1, 32):
            if day <= 5:
                # Beginning of month - high activity
                factor = 1.0
            elif day <= 15:
                # Mid-month - normal activity
                factor = 0.9
            elif day <= 25:
                # Late month - slightly lower
                factor = 0.8
            else:
                # End of month - low activity
                factor = 0.7
            
            # Weekend adjustment
            weekday = datetime(2024, 1, day).weekday()
            if weekday >= 5:  # Saturday, Sunday
                factor *= 0.4
            
            monthly_pattern.append(factor)
        
        return monthly_pattern
    
    def generate_daily_pattern(self, date: datetime, base_users: int = 100) -> Dict:
        """Generate traffic pattern for a specific day"""
        day_of_week = date.weekday()
        weekly_multiplier = self.base_weekly_pattern[day_of_week]
        
        hourly_users = []
        for hour in range(24):
            hourly_multiplier = self.base_hourly_pattern[hour]
            users = int(base_users * weekly_multiplier * hourly_multiplier)
            # Add some randomness
            users = int(users * random.uniform(0.8, 1.2))
            hourly_users.append(max(1, users))
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": day_of_week,
            "weekly_multiplier": weekly_multiplier,
            "hourly_users": hourly_users,
            "total_users": sum(hourly_users),
            "peak_hour": hourly_users.index(max(hourly_users)),
            "peak_users": max(hourly_users)
        }
    
    def generate_weekly_pattern(self, start_date: datetime, base_users: int = 100) -> List[Dict]:
        """Generate traffic pattern for a week"""
        weekly_data = []
        for i in range(7):
            date = start_date + timedelta(days=i)
            daily_data = self.generate_daily_pattern(date, base_users)
            weekly_data.append(daily_data)
        
        return weekly_data
    
    def generate_monthly_pattern(self, year: int, month: int, base_users: int = 100) -> List[Dict]:
        """Generate traffic pattern for a month"""
        monthly_data = []
        
        # Get first day of month
        first_day = datetime(year, month, 1)
        
        # Get number of days in month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        days_in_month = (next_month - first_day).days
        
        for day in range(1, days_in_month + 1):
            date = datetime(year, month, day)
            daily_data = self.generate_daily_pattern(date, base_users)
            monthly_data.append(daily_data)
        
        return monthly_data
    
    def generate_seasonal_pattern(self, year: int, base_users: int = 100) -> List[Dict]:
        """Generate traffic pattern for entire year with seasonal variations"""
        yearly_data = []
        
        # Seasonal multipliers
        seasonal_multipliers = {
            "spring": 1.1,  # March-May
            "summer": 0.9,  # June-August
            "fall": 1.0,    # September-November
            "winter": 0.95  # December-February
        }
        
        for month in range(1, 13):
            if month in [3, 4, 5]:
                season_multiplier = seasonal_multipliers["spring"]
            elif month in [6, 7, 8]:
                season_multiplier = seasonal_multipliers["summer"]
            elif month in [9, 10, 11]:
                season_multiplier = seasonal_multipliers["fall"]
            else:
                season_multiplier = seasonal_multipliers["winter"]
            
            # Adjust base users for season
            seasonal_base_users = int(base_users * season_multiplier)
            
            monthly_data = self.generate_monthly_pattern(year, month, seasonal_base_users)
            yearly_data.extend(monthly_data)
        
        return yearly_data
    
    def generate_burst_pattern(self, base_users: int = 100, burst_factor: float = 3.0, 
                             duration_minutes: int = 30) -> Dict:
        """Generate burst traffic pattern (e.g., marketing campaign)"""
        current_time = datetime.now()
        
        # Generate normal pattern for comparison
        normal_pattern = self.generate_daily_pattern(current_time, base_users)
        
        # Create burst pattern
        burst_pattern = normal_pattern.copy()
        
        # Find current hour
        current_hour = current_time.hour
        
        # Apply burst to current hour and adjacent hours
        for hour_offset in range(-1, 2):  # Previous, current, next hour
            hour_index = (current_hour + hour_offset) % 24
            if hour_offset == 0:
                # Current hour gets full burst
                burst_multiplier = burst_factor
            else:
                # Adjacent hours get partial burst
                burst_multiplier = 1 + (burst_factor - 1) * 0.5
            
            burst_pattern["hourly_users"][hour_index] = int(
                burst_pattern["hourly_users"][hour_index] * burst_multiplier
            )
        
        burst_pattern["total_users"] = sum(burst_pattern["hourly_users"])
        burst_pattern["burst_applied"] = True
        burst_pattern["burst_factor"] = burst_factor
        burst_pattern["burst_duration"] = duration_minutes
        
        return burst_pattern
    
    def generate_gradual_ramp_pattern(self, start_users: int, end_users: int, 
                                    duration_hours: int = 8) -> Dict:
        """Generate gradual ramp-up/ramp-down pattern"""
        current_time = datetime.now()
        
        # Generate base pattern
        base_pattern = self.generate_daily_pattern(current_time, start_users)
        
        # Calculate ramp factor for each hour
        ramp_pattern = base_pattern.copy()
        
        for hour in range(24):
            if hour < duration_hours:
                # Ramp up
                progress = hour / duration_hours
                ramp_factor = 1 + (end_users / start_users - 1) * progress
            else:
                # Maintain end state
                ramp_factor = end_users / start_users
            
            ramp_pattern["hourly_users"][hour] = int(
                ramp_pattern["hourly_users"][hour] * ramp_factor
            )
        
        ramp_pattern["total_users"] = sum(ramp_pattern["hourly_users"])
        ramp_pattern["ramp_applied"] = True
        ramp_pattern["start_users"] = start_users
        ramp_pattern["end_users"] = end_users
        ramp_pattern["duration_hours"] = duration_hours
        
        return ramp_pattern
    
    def analyze_patterns(self, patterns: List[Dict]) -> Dict:
        """Analyze traffic patterns and return statistics"""
        if not patterns:
            return {}
        
        total_users = [p["total_users"] for p in patterns]
        peak_users = [p["peak_users"] for p in patterns]
        
        analysis = {
            "total_days": len(patterns),
            "avg_daily_users": np.mean(total_users),
            "min_daily_users": np.min(total_users),
            "max_daily_users": np.max(total_users),
            "avg_peak_users": np.mean(peak_users),
            "min_peak_users": np.min(peak_users),
            "max_peak_users": np.max(peak_users),
            "peak_hour_distribution": {}
        }
        
        # Analyze peak hour distribution
        peak_hours = [p["peak_hour"] for p in patterns]
        for hour in range(24):
            analysis["peak_hour_distribution"][hour] = peak_hours.count(hour)
        
        return analysis
    
    def export_to_locust_config(self, pattern: Dict, output_file: str = "locust_traffic_config.json"):
        """Export traffic pattern to Locust-compatible configuration"""
        locust_config = {
            "scenarios": [],
            "user_classes": [],
            "traffic_pattern": {
                "date": pattern["date"],
                "total_users": pattern["total_users"],
                "peak_hour": pattern["peak_hour"],
                "peak_users": pattern["peak_users"]
            }
        }
        
        # Create scenarios based on hourly patterns
        for hour, users in enumerate(pattern["hourly_users"]):
            if users > 0:
                scenario_name = f"hour_{hour:02d}_{users}users"
                locust_config["scenarios"].append({
                    "name": scenario_name,
                    "users": users,
                    "spawn_rate": max(1, users // 10),
                    "run_time": "3600s",  # 1 hour
                    "hour": hour
                })
        
        # Add user class weights
        locust_config["user_classes"] = [
            {"name": "BusinessUser", "weight": 60},
            {"name": "CasualUser", "weight": 25},
            {"name": "PowerUser", "weight": 10},
            {"name": "MobileAppUser", "weight": 5}
        ]
        
        with open(output_file, 'w') as f:
            json.dump(locust_config, f, indent=2)
        
        return locust_config
    
    def visualize_pattern(self, pattern: Dict, save_file: str = None):
        """Visualize traffic pattern"""
        hours = list(range(24))
        users = pattern["hourly_users"]
        
        plt.figure(figsize=(12, 6))
        plt.plot(hours, users, marker='o', linewidth=2, markersize=6)
        plt.fill_between(hours, users, alpha=0.3)
        
        plt.title(f'Traffic Pattern for {pattern["date"]}')
        plt.xlabel('Hour of Day')
        plt.ylabel('Number of Users')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24, 2))
        
        # Highlight peak hour
        peak_hour = pattern["peak_hour"]
        peak_users = pattern["peak_users"]
        plt.axvline(x=peak_hour, color='red', linestyle='--', alpha=0.7)
        plt.annotate(f'Peak: {peak_users} users', 
                    xy=(peak_hour, peak_users),
                    xytext=(peak_hour + 1, peak_users + 5),
                    arrowprops=dict(arrowstyle='->', color='red'))
        
        plt.tight_layout()
        
        if save_file:
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()


class LoadTestScenarioGenerator:
    """
    Generates specific load test scenarios based on business requirements
    """
    
    def __init__(self):
        self.traffic_generator = TrafficPatternGenerator()
    
    def generate_business_hours_scenario(self, date: datetime = None) -> Dict:
        """Generate scenario for business hours (9am-5pm)"""
        if date is None:
            date = datetime.now()
        
        pattern = self.traffic_generator.generate_daily_pattern(date, base_users=150)
        
        # Focus on business hours
        business_hours_pattern = pattern.copy()
        for hour in range(24):
            if hour < 9 or hour >= 17:  # Outside business hours
                business_hours_pattern["hourly_users"][hour] = int(
                    business_hours_pattern["hourly_users"][hour] * 0.2
                )
        
        business_hours_pattern["scenario_type"] = "business_hours"
        business_hours_pattern["focus_hours"] = "9am-5pm"
        business_hours_pattern["total_users"] = sum(business_hours_pattern["hourly_users"])
        
        return business_hours_pattern
    
    def generate_weekend_scenario(self, date: datetime = None) -> Dict:
        """Generate scenario for weekend traffic"""
        if date is None:
            # Get next Saturday
            today = datetime.now()
            days_until_saturday = (5 - today.weekday()) % 7
            date = today + timedelta(days=days_until_saturday)
        
        pattern = self.traffic_generator.generate_daily_pattern(date, base_users=50)
        
        # Weekend pattern - more casual usage
        weekend_pattern = pattern.copy()
        
        # Shift peak to later hours
        for hour in range(24):
            if 6 <= hour <= 10:  # Morning
                weekend_pattern["hourly_users"][hour] = int(
                    weekend_pattern["hourly_users"][hour] * 0.5
                )
            elif 18 <= hour <= 22:  # Evening
                weekend_pattern["hourly_users"][hour] = int(
                    weekend_pattern["hourly_users"][hour] * 1.5
                )
        
        weekend_pattern["scenario_type"] = "weekend"
        weekend_pattern["focus_hours"] = "evening"
        weekend_pattern["total_users"] = sum(weekend_pattern["hourly_users"])
        
        return weekend_pattern
    
    def generate_holiday_scenario(self, date: datetime = None) -> Dict:
        """Generate scenario for holiday traffic"""
        if date is None:
            # Use December 25th as example
            date = datetime(datetime.now().year, 12, 25)
        
        pattern = self.traffic_generator.generate_daily_pattern(date, base_users=30)
        
        # Holiday pattern - very low traffic
        holiday_pattern = pattern.copy()
        
        for hour in range(24):
            holiday_pattern["hourly_users"][hour] = int(
                holiday_pattern["hourly_users"][hour] * 0.3
            )
        
        holiday_pattern["scenario_type"] = "holiday"
        holiday_pattern["focus_hours"] = "minimal"
        holiday_pattern["total_users"] = sum(holiday_pattern["hourly_users"])
        
        return holiday_pattern
    
    def generate_product_launch_scenario(self, date: datetime = None) -> Dict:
        """Generate scenario for product launch (high traffic)"""
        if date is None:
            date = datetime.now()
        
        pattern = self.traffic_generator.generate_daily_pattern(date, base_users=500)
        
        # Product launch - very high traffic
        launch_pattern = pattern.copy()
        
        # Amplify all hours
        for hour in range(24):
            launch_pattern["hourly_users"][hour] = int(
                launch_pattern["hourly_users"][hour] * 2.0
            )
        
        launch_pattern["scenario_type"] = "product_launch"
        launch_pattern["focus_hours"] = "all_day"
        launch_pattern["total_users"] = sum(launch_pattern["hourly_users"])
        
        return launch_pattern
    
    def generate_maintenance_scenario(self, date: datetime = None) -> Dict:
        """Generate scenario for maintenance window"""
        if date is None:
            date = datetime.now()
        
        pattern = self.traffic_generator.generate_daily_pattern(date, base_users=20)
        
        # Maintenance - minimal traffic
        maintenance_pattern = pattern.copy()
        
        # Very low traffic during maintenance
        for hour in range(24):
            maintenance_pattern["hourly_users"][hour] = max(1, 
                int(maintenance_pattern["hourly_users"][hour] * 0.1)
            )
        
        maintenance_pattern["scenario_type"] = "maintenance"
        maintenance_pattern["focus_hours"] = "minimal"
        maintenance_pattern["total_users"] = sum(maintenance_pattern["hourly_users"])
        
        return maintenance_pattern


# Example usage and testing
if __name__ == "__main__":
    # Create traffic pattern generator
    generator = TrafficPatternGenerator()
    
    # Generate today's pattern
    today = datetime.now()
    daily_pattern = generator.generate_daily_pattern(today, base_users=100)
    
    print(f"Traffic Pattern for {today.strftime('%Y-%m-%d')}")
    print(f"Total Users: {daily_pattern['total_users']}")
    print(f"Peak Hour: {daily_pattern['peak_hour']}:00 ({daily_pattern['peak_users']} users)")
    
    # Generate weekly pattern
    weekly_pattern = generator.generate_weekly_pattern(today, base_users=100)
    weekly_analysis = generator.analyze_patterns(weekly_pattern)
    
    print(f"\nWeekly Analysis:")
    print(f"Average Daily Users: {weekly_analysis['avg_daily_users']:.1f}")
    print(f"Peak Daily Users: {weekly_analysis['max_daily_users']}")
    
    # Generate scenarios
    scenario_generator = LoadTestScenarioGenerator()
    
    business_scenario = scenario_generator.generate_business_hours_scenario()
    weekend_scenario = scenario_generator.generate_weekend_scenario()
    launch_scenario = scenario_generator.generate_product_launch_scenario()
    
    print(f"\nBusiness Hours Scenario: {business_scenario['total_users']} users")
    print(f"Weekend Scenario: {weekend_scenario['total_users']} users")
    print(f"Product Launch Scenario: {launch_scenario['total_users']} users")
    
    # Export to Locust config
    generator.export_to_locust_config(daily_pattern, "daily_traffic_config.json")
    
    # Visualize pattern
    generator.visualize_pattern(daily_pattern, "traffic_pattern.png")
