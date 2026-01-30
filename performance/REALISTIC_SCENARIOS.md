# Realistic Load Testing Scenarios for Helm AI

This directory contains realistic load testing scenarios that simulate actual user behavior patterns based on real-world SaaS application usage analytics.

## 🎯 Overview

Realistic load testing goes beyond simple user counts to simulate:
- **Real traffic patterns** based on time of day, day of week, and seasonal variations
- **Authentic user behavior** with different user types and their typical workflows
- **Business-relevant scenarios** like product launches, maintenance windows, and traffic bursts
- **Geographic and device distribution** matching real user demographics

## 📁 Files Overview

### Core Scenario Files
- **`realistic_scenarios.py`** - User behavior classes (BusinessUser, CasualUser, PowerUser, MobileAppUser)
- **`traffic_patterns.py`** - Traffic pattern generator with hourly, weekly, and seasonal variations
- **`run_realistic_load_tests.py`** - Main runner for realistic load testing scenarios
- **`realistic_config.py`** - Configuration for realistic scenarios and user behaviors

### Supporting Files
- **`locustfile.py`** - Original Locust test file (basic scenarios)
- **`run_performance_tests.py`** - Original performance test runner
- **`performance_config.py`** - Original performance configuration

## 👥 User Behavior Types

### BusinessUser (60% of traffic)
**Profile**: Professional users accessing during business hours
- **Session Duration**: 15-30 minutes
- **Peak Hours**: 9am-5pm
- **Common Actions**:
  - View dashboard (4x weight)
  - Analyze business data (3x weight)
  - Manage projects (2x weight)
  - Team collaboration (2x weight)
  - Generate reports (1x weight)

### CasualUser (25% of traffic)
**Profile**: Regular users with sporadic usage patterns
- **Session Duration**: 5-15 minutes
- **Peak Hours**: Evenings and weekends
- **Common Actions**:
  - Browse content (5x weight)
  - Search content (3x weight)
  - Interact with content (2x weight)
  - Update profile (1x weight)

### PowerUser (10% of traffic)
**Profile**: Advanced users with heavy automation and API usage
- **Session Duration**: 30-60 minutes
- **Peak Hours**: All day
- **Common Actions**:
  - Advanced analytics (6x weight)
  - API integration (4x weight)
  - Automation workflows (3x weight)
  - Bulk operations (2x weight)
  - System administration (1x weight)

### MobileAppUser (5% of traffic)
**Profile**: Mobile app users with app-specific behaviors
- **Session Duration**: 2-10 minutes
- **Peak Hours**: Evenings
- **Common Actions**:
  - Mobile dashboard (5x weight)
  - Push notifications (3x weight)
  - Mobile features (2x weight)

## 📊 Traffic Patterns

### Hourly Pattern (24-hour cycle)
```
12am-6am: 5-10%  (Low activity)
6am-9am: 30-80%  (Morning ramp-up)
9am-11am: 100%   (Peak morning)
11am-1pm: 70-80%  (Lunch dip)
2pm-4pm: 80-90%   (Afternoon peak)
4pm-6pm: 40-60%  (Evening wind-down)
6pm-9pm: 15-30%  (Evening casual)
9pm-12am: 5-10%  (Night activity)
```

### Weekly Pattern
- **Monday**: 100% (Highest)
- **Tuesday**: 95%
- **Wednesday**: 90%
- **Thursday**: 85%
- **Friday**: 80%
- **Saturday**: 40%
- **Sunday**: 30% (Lowest)

### Seasonal Pattern
- **Spring**: 110% (Mar-May)
- **Summer**: 90% (Jun-Aug)
- **Fall**: 100% (Sep-Nov)
- **Winter**: 95% (Dec-Feb)

## 🎬 Testing Scenarios

### 1. Daily Pattern Test
**Purpose**: Simulate normal daily traffic with hourly variations
```bash
python run_realistic_load_tests.py --scenario daily_pattern
```

**Features**:
- 24-hour traffic pattern
- All user types with normal distribution
- Realistic timing and user behavior
- Hourly test execution

### 2. Business Hours Test
**Purpose**: Focus on peak business hours (9am-5pm)
```bash
python run_realistic_load_tests.py --scenario business_hours
```

**Features**:
- Concentrated testing during 9am-5pm
- Higher BusinessUser percentage (70%)
- Professional workflow focus
- Lunch dip simulation

### 3. Weekend Pattern Test
**Purpose**: Simulate weekend traffic patterns
```bash
python run_realistic_load_tests.py --scenario weekend_pattern
```

**Features**:
- Weekend date selection
- Evening peak focus
- Higher CasualUser percentage (50%)
- Mobile app emphasis

### 4. Product Launch Test
**Purpose**: High traffic scenario for product launches
```bash
python run_realistic_load_tests.py --scenario product_launch
```

**Features**:
- 2x traffic multiplier
- All-day high activity
- Mixed user distribution
- Shorter test durations

### 5. Burst Traffic Test
**Purpose**: Sudden traffic surge simulation
```bash
python run_realistic_load_tests.py --scenario burst_traffic --burst-factor 3.0 --burst-duration 30
```

**Features**:
- Configurable burst multiplier (default 3x)
- Short duration bursts (default 30 minutes)
- Current hour focus
- Stress testing capability

### 6. Gradual Ramp Test
**Purpose**: Gradual user ramp-up scenario
```bash
python run_realistic_load_tests.py --scenario gradual_ramp --ramp-start 50 --ramp-end 200 --ramp-hours 4
```

**Features**:
- Smooth user count increase
- Configurable start/end users
- Extended duration testing
- Capacity planning focus

## 🚀 Usage Examples

### Basic Usage
```bash
# Run daily pattern test
python run_realistic_load_tests.py --scenario daily_pattern

# Run business hours test for specific date
python run_realistic_load_tests.py --scenario business_hours --date 2024-03-15

# Run all scenarios
python run_realistic_load_tests.py --all
```

### Advanced Usage
```bash
# Custom host and user count
python run_realistic_load_tests.py --scenario daily_pattern --host http://staging.helm-ai.com --base-users 200

# Custom burst test
python run_realistic_load_tests.py --scenario burst_traffic --burst-factor 5.0 --burst-duration 45

# Custom ramp test
python run_realistic_load_tests.py --scenario gradual_ramp --ramp-start 100 --ramp-end 500 --ramp-hours 6
```

### Configuration Override
```bash
# Use custom configuration
python run_realistic_load_tests.py --config custom_config.py --scenario daily_pattern
```

## 📈 Results and Analysis

### Output Files
- **`realistic_results/`** - JSON results and CSV data
- **`realistic_reports/`** - HTML reports and visualizations
- **`realistic_load_tests.log`** - Detailed execution logs

### Metrics Tracked
- **Response Times**: Average, median, 95th percentile
- **Error Rates**: By endpoint and user type
- **Throughput**: Requests per second
- **User Journeys**: Action sequences and timing
- **Resource Usage**: CPU, memory, network

### Analysis Features
- **Pattern Comparison**: Daily vs weekend vs business hours
- **User Behavior Analysis**: Action frequency and timing
- **Performance Trends**: Response time patterns
- **Bottleneck Detection**: Slow endpoints and user actions
- **Capacity Planning**: User count vs performance correlation

## 🔧 Configuration

### User Distribution
```python
"user_distribution": {
    "BusinessUser": 60,
    "CasualUser": 25,
    "PowerUser": 10,
    "MobileAppUser": 5
}
```

### Traffic Multipliers
```python
"hourly_multipliers": {
    "business_hours": {
        "9am-11am": 1.0,
        "2pm-4pm": 0.9
    }
}
```

### Thresholds
```python
"thresholds": {
    "response_time": {
        "warning": 1000,  # ms
        "critical": 2000  # ms
    },
    "error_rate": {
        "warning": 0.01,  # 1%
        "critical": 0.05  # 5%
    }
}
```

## 📊 Traffic Pattern Visualization

The framework includes built-in visualization capabilities:

```python
from traffic_patterns import TrafficPatternGenerator

generator = TrafficPatternGenerator()
pattern = generator.generate_daily_pattern(datetime.now(), base_users=100)
generator.visualize_pattern(pattern, "daily_pattern.png")
```

### Available Visualizations
- **Hourly Traffic Patterns**: 24-hour user count graphs
- **Weekly Comparisons**: Day-by-day traffic analysis
- **Seasonal Trends**: Monthly and yearly patterns
- **User Journey Maps**: Action sequence flows
- **Performance Heatmaps**: Response time by hour and user type

## 🎯 Business Use Cases

### 1. Capacity Planning
- **Scenario**: Gradual ramp test with increasing user counts
- **Purpose**: Determine system capacity and scaling requirements
- **Metrics**: Response time degradation, error rate increase

### 2. Marketing Campaign Testing
- **Scenario**: Burst traffic test with 3-5x multiplier
- **Purpose**: Prepare for marketing-driven traffic spikes
- **Metrics**: System stability under sudden load

### 3. Product Launch Preparation
- **Scenario**: Product launch test with 2x sustained traffic
- **Purpose**: Ensure system handles launch-day traffic
- **Metrics**: Consistent performance under high load

### 4. Maintenance Window Validation
- **Scenario**: Maintenance window test with 10% traffic
- **Purpose**: Verify system stability during maintenance
- **Metrics**: Core functionality availability

### 5. Geographic Expansion Testing
- **Scenario**: Custom user distribution by region
- **Purpose**: Test performance for new geographic markets
- **Metrics**: Regional response time differences

## 🔍 Monitoring and Alerting

### Real-time Monitoring
```python
"monitoring": {
    "enable_metrics": True,
    "metrics_interval": 30,
    "save_user_journeys": True,
    "track_response_times": True
}
```

### Alert Thresholds
- **Response Time**: >1000ms (warning), >2000ms (critical)
- **Error Rate**: >1% (warning), >5% (critical)
- **Throughput**: <50 req/s (warning)
- **User Satisfaction**: <95% (warning), <90% (critical)

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Realistic Load Tests
  run: |
    cd performance
    python run_realistic_load_tests.py --scenario daily_pattern --host $STAGING_URL
    python run_realistic_load_tests.py --scenario business_hours --host $STAGING_URL
```

### Automated Reporting
- **Slack Integration**: Real-time test results
- **Email Summaries**: Daily/weekly performance reports
- **Dashboard Updates**: Grafana/Chronograf integration
- **Alert Notifications**: Threshold breach alerts

## 📚 Best Practices

### Test Planning
1. **Start with daily patterns** to establish baseline
2. **Progress to complex scenarios** for comprehensive testing
3. **Use realistic user counts** based on actual analytics
4. **Test during appropriate times** (business hours vs off-hours)

### Data Analysis
1. **Compare patterns** to identify anomalies
2. **Track trends over time** for performance degradation
3. **Correlate with code changes** for regression detection
4. **Focus on user experience** metrics

### Continuous Improvement
1. **Update patterns** based on real user analytics
2. **Refine user behaviors** with actual usage data
3. **Adjust thresholds** based on business requirements
4. **Expand scenarios** for new features and workflows

## 🤝 Contributing

When adding new realistic scenarios:

1. **Analyze real user data** for authentic patterns
2. **Create appropriate user classes** with realistic behaviors
3. **Validate against analytics** for accuracy
4. **Document business context** and use cases
5. **Test thoroughly** before integration

## 📞 Support

For realistic load testing issues:

1. **Check traffic pattern logs** in `realistic_load_tests.log`
2. **Verify user behavior data** in JSON results
3. **Review configuration** in `realistic_config.py`
4. **Consult visualization charts** for pattern analysis
5. **Contact the performance team** for complex scenarios

---

**Realistic load testing provides the most accurate simulation of actual user behavior, ensuring your Helm AI application performs optimally under real-world conditions.**
