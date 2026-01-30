# Helm AI Performance Testing Framework

This directory contains a comprehensive performance testing framework for the Helm AI application using Locust.

## 📁 Files Overview

- **`locustfile.py`** - Main Locust test file with user behavior scenarios
- **`run_performance_tests.py`** - Python script to orchestrate performance tests
- **`performance_config.py`** - Configuration file with test scenarios and thresholds
- **`locust.conf`** - Locust configuration file
- **`requirements.txt`** - Python dependencies for performance testing
- **`README.md`** - This documentation file

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd performance
pip install -r requirements.txt
```

### 2. Start the Helm AI Application

Make sure your Helm AI application is running on `http://localhost:5000` or update the host in the configuration.

### 3. Run a Quick Smoke Test

```bash
python run_performance_tests.py --smoke --host http://localhost:5000
```

### 4. Run All Scenarios

```bash
python run_performance_tests.py --all --host http://localhost:5000
```

## 📊 Test Scenarios

### Available Scenarios

| Scenario | Users | Duration | Description |
|----------|-------|----------|-------------|
| **smoke** | 10 | 60s | Quick functionality verification |
| **load** | 50 | 5min | Normal traffic simulation |
| **stress** | 200 | 10min | System limit testing |
| **spike** | 500 | 2min | Traffic surge simulation |
| **endurance** | 30 | 1hr | Long-running stability |
| **api_focus** | 100 | 5min | API endpoint testing |
| **mobile_focus** | 25 | 3min | Mobile app testing |
| **admin_focus** | 5 | 2min | Admin panel testing |

### User Types

- **Regular Users** (70%) - Standard web application users
- **API Users** (20%) - API-only integration users
- **Mobile Users** (5%) - Mobile app users
- **Admin Users** (5%) - Administrative users

## 🛠️ Usage Examples

### Basic Commands

```bash
# Run smoke test
python run_performance_tests.py --smoke

# Run load test with custom host
python run_performance_tests.py --load --host http://staging.helm-ai.com

# Run specific scenario
python run_performance_tests.py --scenario stress --user-type mixed

# Check server health only
python run_performance_tests.py --check-health

# Run all scenarios
python run_performance_tests.py --all
```

### Using Locust Directly

```bash
# Start Locust web interface
locust -f locustfile.py --host http://localhost:5000

# Run headless test
locust -f locustfile.py --host http://localhost:5000 --users 50 --spawn-rate 5 --run-time 300s --headless

# Run with specific user class
locust -f locustfile.py --host http://localhost:5000 --user-class APIUser --users 100 --spawn-rate 10 --headless
```

## 📈 Performance Thresholds

The framework monitors these performance thresholds:

- **Response Time**: Warning at 1000ms, Critical at 2000ms
- **Error Rate**: Warning at 1%, Critical at 5%
- **Throughput**: Minimum 100 req/s, Warning below 50 req/s

## 📊 Results and Reports

Test results are saved in the following directories:

- **`results/`** - CSV files and raw test data
- **`reports/`** - HTML reports and visualizations
- **`logs/`** - Detailed execution logs

### Report Types

- **HTML Reports** - Interactive performance dashboards
- **CSV Data** - Raw metrics for analysis
- **JSON Summaries** - Structured test results
- **Charts** - Response time and throughput graphs

## 🔧 Configuration

### Customizing Scenarios

Edit `performance_config.py` to modify:

```python
"scenarios": {
    "custom_test": {
        "users": 75,
        "spawn_rate": 15,
        "run_time": "180s",
        "description": "Custom test scenario"
    }
}
```

### Adjusting Thresholds

```python
"thresholds": {
    "response_time": {
        "warning": 500,    # ms
        "critical": 1000   # ms
    },
    "error_rate": {
        "warning": 0.005,  # 0.5%
        "critical": 0.02   # 2%
    }
}
```

## 🧪 User Behavior Simulation

### Regular User (HelmAIUser)

- Views dashboard (3x weight)
- Gets user profile (2x weight)
- Gets analytics data (2x weight)
- Updates settings (1x weight)
- Creates projects (1x weight)
- Searches functionality (1x weight)

### API User (APIUser)

- Tracks analytics events (5x weight)
- Exports data (3x weight)
- Handles webhooks (2x weight)
- Health checks (1x weight)

### Admin User (AdminUser)

- System status monitoring (3x weight)
- User statistics (2x weight)
- Performance metrics (2x weight)
- Error log viewing (1x weight)
- User management (1x weight)

### Mobile User (MobileUser)

- Mobile dashboard (4x weight)
- Push notifications (2x weight)

### Enterprise User (EnterpriseUser)

- Enterprise dashboard (3x weight)
- Team management (2x weight)
- Billing information (2x weight)
- Compliance reports (1x weight)

## 📊 Monitoring and Metrics

### Real-time Metrics

- Response times
- Request rates
- Error rates
- User counts
- Memory usage
- CPU usage

### Post-test Analysis

- Performance trends
- Bottleneck identification
- Capacity planning
- SLA compliance

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Helm AI app is running
   - Check host configuration
   - Verify port accessibility

2. **High Error Rates**
   - Check application logs
   - Verify authentication tokens
   - Monitor system resources

3. **Slow Response Times**
   - Check database performance
   - Monitor memory usage
   - Review application logs

### Debug Mode

Enable debug logging:

```bash
python run_performance_tests.py --smoke --debug
```

## 🔄 Continuous Integration

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run Performance Tests
  run: |
    cd performance
    python run_performance_tests.py --smoke --host $TEST_URL
```

### Automated Alerts

The framework can be configured to send alerts when thresholds are exceeded.

## 📚 Best Practices

### Test Planning

1. **Start with smoke tests** to verify basic functionality
2. **Gradually increase load** to find breaking points
3. **Test different user types** to simulate realistic traffic
4. **Monitor system resources** during tests
5. **Document baseline performance** for comparison

### Test Environment

1. **Use dedicated test environment**
2. **Ensure consistent configuration**
3. **Monitor external dependencies**
4. **Clear caches between tests**
5. **Use realistic data volumes**

### Analysis

1. **Compare results across scenarios**
2. **Identify performance regressions**
3. **Track trends over time**
4. **Correlate with code changes**
5. **Plan capacity based on results**

## 🤝 Contributing

When adding new test scenarios:

1. Update `performance_config.py`
2. Add user behavior to `locustfile.py`
3. Update documentation
4. Test the new scenario
5. Update thresholds if needed

## 📞 Support

For performance testing issues:

1. Check the logs in `logs/` directory
2. Review the configuration files
3. Verify the target application is running
4. Consult the Locust documentation
5. Contact the development team

## 📄 License

This performance testing framework is part of the Helm AI project and follows the same licensing terms.
