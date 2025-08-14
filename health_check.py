#!/usr/bin/env python3
"""
FinRisk Production Health Check Script
Verifies that all components are running correctly in production.
"""

import requests
import json
import sys
import time
from datetime import datetime

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🏥 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def print_warning(message):
    """Print a warning message."""
    print(f"⚠️  {message}")

def check_api_health(base_url="http://localhost:8000"):
    """Check API health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API Health: {data.get('status', 'unknown')}")
            print(f"   Service: {data.get('service', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            return True
        else:
            print_error(f"API Health failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API Health check failed: {str(e)}")
        return False

def check_api_docs(base_url="http://localhost:8000"):
    """Check API documentation endpoint."""
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print_success("API Documentation accessible")
            return True
        else:
            print_error(f"API Documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API Documentation check failed: {str(e)}")
        return False

def check_metrics(base_url="http://localhost:8000"):
    """Check Prometheus metrics endpoint."""
    try:
        response = requests.get(f"{base_url}/metrics", timeout=10)
        if response.status_code == 200:
            print_success("Prometheus metrics accessible")
            return True
        else:
            print_error(f"Metrics endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Metrics check failed: {str(e)}")
        return False

def test_credit_assessment(base_url="http://localhost:8000"):
    """Test credit risk assessment endpoint."""
    try:
        payload = {
            "customer_id": "HEALTH_CHECK_001",
            "loan_amount": 50000,
            "annual_income": 75000,
            "debt_to_income_ratio": 0.35,
            "credit_score": 720,
            "employment_status": "Full-time",
            "years_employed": 5
        }
        
        response = requests.post(
            f"{base_url}/api/credit/assess",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Credit Assessment endpoint working")
            print(f"   Decision: {data.get('decision', 'unknown')}")
            print(f"   Risk Score: {data.get('risk_score', 'unknown')}")
            print(f"   Processing Time: {data.get('processing_time_ms', 'unknown')}ms")
            return True
        else:
            print_error(f"Credit Assessment failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Credit Assessment test failed: {str(e)}")
        return False

def test_fraud_detection(base_url="http://localhost:8000"):
    """Test fraud detection endpoint."""
    try:
        payload = {
            "customer_id": "HEALTH_CHECK_001",
            "transaction_id": "TXN_HEALTH_001",
            "amount": 2500,
            "merchant_category": "Electronics",
            "location": "New York, USA",
            "device_info": "Mobile Device"
        }
        
        response = requests.post(
            f"{base_url}/api/fraud/detect",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Fraud Detection endpoint working")
            print(f"   Decision: {data.get('decision', 'unknown')}")
            print(f"   Fraud Probability: {data.get('fraud_probability', 'unknown')}")
            print(f"   Processing Time: {data.get('processing_time_ms', 'unknown')}ms")
            return True
        else:
            print_error(f"Fraud Detection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Fraud Detection test failed: {str(e)}")
        return False

def check_response_times(base_url="http://localhost:8000"):
    """Check API response times."""
    endpoints = [
        ("/health", "GET"),
        ("/api/credit/assess", "POST"),
        ("/api/fraud/detect", "POST")
    ]
    
    print_header("Response Time Check")
    
    for endpoint, method in endpoints:
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                # Use minimal payload for POST requests
                payload = {"test": "health_check"}
                response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=10)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code < 500:  # Accept any non-server error
                if response_time < 1000:
                    print_success(f"{endpoint}: {response_time:.1f}ms")
                elif response_time < 3000:
                    print_warning(f"{endpoint}: {response_time:.1f}ms (slow)")
                else:
                    print_error(f"{endpoint}: {response_time:.1f}ms (very slow)")
            else:
                print_error(f"{endpoint}: Failed ({response.status_code})")
                
        except Exception as e:
            print_error(f"{endpoint}: Error - {str(e)}")

def main():
    """Run all health checks."""
    print_header("FinRisk Production Health Check")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print(f"Checking API at: {base_url}")
    
    checks = [
        ("API Health", lambda: check_api_health(base_url)),
        ("API Documentation", lambda: check_api_docs(base_url)),
        ("Prometheus Metrics", lambda: check_metrics(base_url)),
        ("Credit Assessment", lambda: test_credit_assessment(base_url)),
        ("Fraud Detection", lambda: test_fraud_detection(base_url)),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print_header(f"Testing {check_name}")
        try:
            if check_func():
                passed += 1
            else:
                print_error(f"{check_name} check failed")
        except Exception as e:
            print_error(f"{check_name} check crashed: {str(e)}")
    
    # Check response times
    check_response_times(base_url)
    
    print_header("Health Check Summary")
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("🎉 All health checks passed! FinRisk is running correctly.")
        print_success("✅ API is healthy and ready for production use.")
        sys.exit(0)
    else:
        print_error("❌ Some health checks failed. Please investigate the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
