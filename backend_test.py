#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Web Application Penetration Testing Tool
Tests all endpoints including scan creation, retrieval, deletion, and report download
"""

import requests
import sys
import time
import json
from datetime import datetime
from pathlib import Path

class PenTestAPITester:
    def __init__(self, base_url="https://pentest-dashboard-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.scan_id = None
        self.session = requests.Session()
        self.session.timeout = 30

    def log(self, message):
        """Log with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
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
                try:
                    error_detail = response.json()
                    self.log(f"   Error details: {error_detail}")
                except:
                    self.log(f"   Response text: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            self.log(f"❌ Failed - Request timeout after {timeout}s")
            return False, {}
        except Exception as e:
            self.log(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        if success and 'message' in response:
            self.log(f"   API Message: {response['message']}")
        return success

    def test_owasp_categories(self):
        """Test OWASP categories endpoint"""
        success, response = self.run_test(
            "OWASP Categories",
            "GET", 
            "owasp-categories",
            200
        )
        if success:
            categories = list(response.keys()) if response else []
            self.log(f"   Found {len(categories)} OWASP categories: {categories[:5]}...")
            # Verify expected OWASP 2025 categories
            expected_categories = ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"]
            missing = [cat for cat in expected_categories if cat not in categories]
            if missing:
                self.log(f"   ⚠️  Missing categories: {missing}")
        return success

    def test_create_scan(self, target_url="https://example.com"):
        """Test scan creation"""
        success, response = self.run_test(
            "Create Scan",
            "POST",
            "scans",
            200,
            data={"target_url": target_url}
        )
        if success and 'id' in response:
            self.scan_id = response['id']
            self.log(f"   Scan ID: {self.scan_id}")
            self.log(f"   Status: {response.get('status', 'unknown')}")
        return success

    def test_get_scan(self, scan_id=None):
        """Test getting specific scan"""
        if not scan_id:
            scan_id = self.scan_id
        if not scan_id:
            self.log("❌ No scan ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Specific Scan",
            "GET",
            f"scans/{scan_id}",
            200
        )
        if success:
            self.log(f"   Target URL: {response.get('target_url', 'unknown')}")
            self.log(f"   Status: {response.get('status', 'unknown')}")
            self.log(f"   Progress: {response.get('progress', 0)}%")
            self.log(f"   Vulnerabilities: {response.get('vulnerabilities_found', 0)}")
        return success

    def test_get_all_scans(self):
        """Test getting all scans"""
        success, response = self.run_test(
            "Get All Scans",
            "GET",
            "scans",
            200
        )
        if success:
            scan_count = len(response) if isinstance(response, list) else 0
            self.log(f"   Found {scan_count} scans")
            if scan_count > 0:
                latest_scan = response[0] if response else {}
                self.log(f"   Latest scan: {latest_scan.get('target_url', 'unknown')} - {latest_scan.get('status', 'unknown')}")
        return success

    def wait_for_scan_completion(self, scan_id=None, max_wait=120):
        """Wait for scan to complete"""
        if not scan_id:
            scan_id = self.scan_id
        if not scan_id:
            self.log("❌ No scan ID available for waiting")
            return False

        self.log(f"⏳ Waiting for scan {scan_id} to complete (max {max_wait}s)...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            success, response = self.run_test(
                "Check Scan Progress",
                "GET",
                f"scans/{scan_id}",
                200
            )
            
            if success:
                status = response.get('status', 'unknown')
                progress = response.get('progress', 0)
                self.log(f"   Status: {status}, Progress: {progress}%")
                
                if status in ['completed', 'failed']:
                    if status == 'completed':
                        self.log(f"✅ Scan completed successfully!")
                        self.log(f"   Pages crawled: {response.get('pages_crawled', 0)}")
                        self.log(f"   Vulnerabilities found: {response.get('vulnerabilities_found', 0)}")
                        return True
                    else:
                        self.log(f"❌ Scan failed")
                        return False
            
            time.sleep(5)  # Wait 5 seconds before checking again
        
        self.log(f"⏰ Scan did not complete within {max_wait}s")
        return False

    def test_download_report(self, scan_id=None):
        """Test PDF report download"""
        if not scan_id:
            scan_id = self.scan_id
        if not scan_id:
            self.log("❌ No scan ID available for report download")
            return False

        self.log(f"📄 Testing PDF report download for scan {scan_id}...")
        
        try:
            url = f"{self.api_url}/scans/{scan_id}/report"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                if response.headers.get('content-type') == 'application/pdf':
                    content_length = len(response.content)
                    self.log(f"✅ PDF report downloaded successfully ({content_length} bytes)")
                    self.tests_passed += 1
                    return True
                else:
                    self.log(f"❌ Expected PDF, got {response.headers.get('content-type')}")
            elif response.status_code == 400:
                self.log(f"⚠️  Scan not completed yet (400 status)")
            elif response.status_code == 404:
                self.log(f"❌ Report not found (404 status)")
            else:
                self.log(f"❌ Unexpected status: {response.status_code}")
                
            self.tests_run += 1
            return False
            
        except Exception as e:
            self.log(f"❌ Report download failed: {str(e)}")
            self.tests_run += 1
            return False

    def test_delete_scan(self, scan_id=None):
        """Test scan deletion"""
        if not scan_id:
            scan_id = self.scan_id
        if not scan_id:
            self.log("❌ No scan ID available for deletion")
            return False

        success, response = self.run_test(
            "Delete Scan",
            "DELETE",
            f"scans/{scan_id}",
            200
        )
        if success:
            self.log(f"   Message: {response.get('message', 'Deleted')}")
        return success

    def test_invalid_url_scan(self):
        """Test scan creation with invalid URL"""
        success, response = self.run_test(
            "Create Scan with Invalid URL",
            "POST",
            "scans",
            400,  # Expecting 400 Bad Request
            data={"target_url": "not-a-valid-url"}
        )
        return success

    def test_nonexistent_scan(self):
        """Test getting non-existent scan"""
        fake_id = "nonexistent-scan-id-12345"
        success, response = self.run_test(
            "Get Non-existent Scan",
            "GET",
            f"scans/{fake_id}",
            404  # Expecting 404 Not Found
        )
        return success

def main():
    """Main test execution"""
    print("=" * 80)
    print("🔒 Web Application Penetration Testing API - Backend Tests")
    print("=" * 80)
    
    # Initialize tester
    tester = PenTestAPITester()
    
    # Test sequence
    test_results = []
    
    # 1. Basic API tests
    print("\n📡 Testing Basic API Endpoints...")
    test_results.append(("Root API", tester.test_root_endpoint()))
    test_results.append(("OWASP Categories", tester.test_owasp_categories()))
    
    # 2. Scan lifecycle tests
    print("\n🔍 Testing Scan Lifecycle...")
    test_results.append(("Create Scan", tester.test_create_scan()))
    test_results.append(("Get Specific Scan", tester.test_get_scan()))
    test_results.append(("Get All Scans", tester.test_get_all_scans()))
    
    # 3. Wait for scan completion (if scan was created successfully)
    if tester.scan_id:
        print(f"\n⏳ Waiting for scan completion...")
        scan_completed = tester.wait_for_scan_completion()
        test_results.append(("Scan Completion", scan_completed))
        
        # 4. Test report download (only if scan completed)
        if scan_completed:
            test_results.append(("Download PDF Report", tester.test_download_report()))
    
    # 5. Error handling tests
    print("\n🚫 Testing Error Handling...")
    test_results.append(("Invalid URL Scan", tester.test_invalid_url_scan()))
    test_results.append(("Non-existent Scan", tester.test_nonexistent_scan()))
    
    # 6. Cleanup - delete test scan
    if tester.scan_id:
        print(f"\n🗑️  Cleaning up...")
        test_results.append(("Delete Scan", tester.test_delete_scan()))
    
    # Print results summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\n📈 Overall: {tester.tests_passed}/{tester.tests_run} tests passed")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    # Return appropriate exit code
    if success_rate >= 80:
        print("\n🎉 Backend API tests completed successfully!")
        return 0
    else:
        print("\n⚠️  Some backend API tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())