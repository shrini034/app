#!/usr/bin/env python3
"""
Quick Backend Test - Test core functionality without waiting for AI analysis
"""

import requests
import sys
import time
import json
from datetime import datetime

class QuickAPITester:
    def __init__(self, base_url="https://pentest-dashboard-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.scan_id = None
        self.session = requests.Session()

    def log(self, message):
        """Log with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=10):
        """Run a single API test with shorter timeout"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.log(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                return False, {}

        except requests.exceptions.Timeout:
            self.log(f"❌ Failed - Request timeout after {timeout}s")
            return False, {}
        except Exception as e:
            self.log(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_endpoints(self):
        """Test basic endpoints that should be fast"""
        results = []
        
        # Root API
        success, _ = self.run_test("Root API", "GET", "", 200)
        results.append(("Root API", success))
        
        # OWASP Categories
        success, response = self.run_test("OWASP Categories", "GET", "owasp-categories", 200)
        if success:
            self.log(f"   Found {len(response)} OWASP categories")
        results.append(("OWASP Categories", success))
        
        return results

    def test_scan_creation(self):
        """Test scan creation with fast URL"""
        success, response = self.run_test(
            "Create Scan (httpbin.org)",
            "POST",
            "scans",
            200,
            data={"target_url": "https://httpbin.org"}
        )
        if success and 'id' in response:
            self.scan_id = response['id']
            self.log(f"   Scan ID: {self.scan_id}")
        return success

    def test_scan_retrieval(self):
        """Test getting the created scan"""
        if not self.scan_id:
            return False
            
        success, response = self.run_test(
            "Get Scan Details",
            "GET",
            f"scans/{self.scan_id}",
            200,
            timeout=15
        )
        if success:
            self.log(f"   Status: {response.get('status', 'unknown')}")
            self.log(f"   Progress: {response.get('progress', 0)}%")
        return success

    def test_scan_list(self):
        """Test getting scan list"""
        success, response = self.run_test(
            "Get Scan List",
            "GET",
            "scans",
            200,
            timeout=15
        )
        if success:
            count = len(response) if isinstance(response, list) else 0
            self.log(f"   Found {count} scans")
        return success

def main():
    """Main test execution"""
    print("🚀 Quick Backend API Test - Core Functionality")
    print("=" * 60)
    
    tester = QuickAPITester()
    all_results = []
    
    # Test basic endpoints
    print("\n📡 Testing Basic Endpoints...")
    basic_results = tester.test_basic_endpoints()
    all_results.extend(basic_results)
    
    # Test scan creation
    print("\n🔍 Testing Scan Creation...")
    scan_created = tester.test_scan_creation()
    all_results.append(("Create Scan", scan_created))
    
    # Test scan retrieval
    print("\n📋 Testing Scan Retrieval...")
    scan_retrieved = tester.test_scan_retrieval()
    all_results.append(("Get Scan Details", scan_retrieved))
    
    # Test scan list
    scan_list = tester.test_scan_list()
    all_results.append(("Get Scan List", scan_list))
    
    # Results
    print("\n" + "=" * 60)
    print("📊 QUICK TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in all_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}% ({tester.tests_passed}/{tester.tests_run})")
    
    return 0 if success_rate >= 60 else 1

if __name__ == "__main__":
    sys.exit(main())