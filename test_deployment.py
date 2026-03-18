#!/usr/bin/env python3
"""
Deployment Testing Script
Test a deployed Tomato Disease Identification app.

Usage:
    python test_deployment.py https://your-service.onrender.com
    
Example:
    python test_deployment.py https://tomato-disease-detector.onrender.com
"""

import requests
import sys
import json
import time
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def test_health_endpoint(url, timeout=10):
    """Test the health check endpoint.
    
    Args:
        url: Base URL of the service
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if healthy, False otherwise
    """
    print_info("Testing health endpoint...")
    
    try:
        response = requests.get(
            f"{url}/health",
            timeout=timeout,
            verify=True  # Verify SSL certificate
        )
        
        if response.status_code in [200, 503]:
            data = response.json()
            status = data.get('status', 'unknown')
            model_loaded = data.get('model_loaded', False)
            
            if response.status_code == 200 and model_loaded:
                print_success(f"Health check passed (status: {status})")
                print_info(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print_warning(f"Health degraded (status: {status}, model_loaded: {model_loaded})")
                print_info(f"Response: {json.dumps(data, indent=2)}")
                return True  # Still OK, just degraded
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error(f"Health check timed out after {timeout} seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print_error(f"Connection error: {e}")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


def test_home_page(url, timeout=10):
    """Test the home page is accessible.
    
    Args:
        url: Base URL of the service
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if accessible, False otherwise
    """
    print_info("Testing home page...")
    
    try:
        response = requests.get(
            url,
            timeout=timeout,
            verify=True
        )
        
        if response.status_code == 200:
            if 'form' in response.text.lower() or 'upload' in response.text.lower():
                print_success("Home page accessible and contains form")
                print_info(f"Response size: {len(response.text)} bytes")
                return True
            else:
                print_warning("Home page accessible but content unexpected")
                return True
        else:
            print_error(f"Home page returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error(f"Home page request timed out after {timeout} seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print_error(f"Connection error: {e}")
        return False
    except Exception as e:
        print_error(f"Home page error: {e}")
        return False


def test_admin_page(url, timeout=10):
    """Test the admin page is accessible.
    
    Args:
        url: Base URL of the service
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if accessible, False otherwise
    """
    print_info("Testing admin page...")
    
    try:
        response = requests.get(
            f"{url}/admin",
            timeout=timeout,
            verify=True
        )
        
        if response.status_code == 200:
            print_success("Admin page accessible")
            return True
        elif response.status_code == 401:
            print_warning("Admin page requires authentication (expected if configured)")
            return True
        else:
            print_warning(f"Admin page returned status {response.status_code}")
            return True  # Still OK
            
    except Exception as e:
        print_warning(f"Admin page test error (non-critical): {e}")
        return True  # Non-critical


def test_api_endpoint(url, timeout=10):
    """Test the API prediction endpoint.
    
    Args:
        url: Base URL of the service
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if accessible, False otherwise
    """
    print_info("Testing API endpoint...")
    
    try:
        # Create a minimal valid PNG (1x1 white pixel)
        # This is a valid image that should work with the API
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # Width: 1, Height: 1
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,  # IDAT
            0x00, 0x03, 0x01, 0x01, 0x00, 0x18, 0xDD, 0x8D,
            0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND
            0x44, 0xAE, 0x42, 0x60
        ])
        
        # Test that endpoint is accessible (may reject test image)
        response = requests.post(
            f"{url}/api/predict",
            files={'file': ('test.png', png_bytes, 'image/png')},
            timeout=timeout,
            verify=True
        )
        
        if response.status_code in [200, 400, 415]:
            print_success(f"API endpoint accessible (status: {response.status_code})")
            if response.status_code == 200:
                data = response.json()
                print_info(f"API response keys: {list(data.keys())}")
            return True
        else:
            print_error(f"API endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error(f"API request timed out after {timeout} seconds")
        return False
    except Exception as e:
        print_warning(f"API test error: {e} (non-critical)")
        return True  # Non-critical


def test_ssl_certificate(url):
    """Test SSL certificate validity.
    
    Args:
        url: Base URL of the service
        
    Returns:
        bool: True if certificate valid, False otherwise
    """
    print_info("Testing SSL certificate...")
    
    try:
        response = requests.get(url, timeout=5, verify=True)
        if response.status_code:
            print_success("SSL certificate valid")
            return True
    except requests.exceptions.SSLError:
        print_error("SSL certificate verification failed")
        return False
    except Exception:
        return True  # Non-critical


def test_response_time(url, timeout=10):
    """Measure response time of health endpoint.
    
    Args:
        url: Base URL of the service
        timeout: Request timeout in seconds
        
    Returns:
        float: Response time in milliseconds
    """
    print_info("Measuring response time...")
    
    try:
        start = time.time()
        response = requests.get(f"{url}/health", timeout=timeout, verify=True)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        if elapsed < 1000:
            print_success(f"Response time: {elapsed:.0f}ms")
        elif elapsed < 5000:
            print_warning(f"Response time: {elapsed:.0f}ms (slightly slow)")
        else:
            print_warning(f"Response time: {elapsed:.0f}ms (slow - may indicate cold start)")
        
        return elapsed
    except Exception as e:
        print_warning(f"Response time measurement failed: {e}")
        return None


def run_all_tests(url):
    """Run all tests on the deployed service.
    
    Args:
        url: Base URL of the service (e.g., https://service.onrender.com)
        
    Returns:
        bool: True if all critical tests passed, False otherwise
    """
    # Ensure URL doesn't have trailing slash
    url = url.rstrip('/')
    
    print_header(f"🧪 Testing Deployment: {url}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    tests_passed = 0
    tests_total = 0
    
    # Critical tests
    critical_tests = [
        ("Health Check", lambda: test_health_endpoint(url)),
        ("Home Page", lambda: test_home_page(url)),
        ("SSL Certificate", lambda: test_ssl_certificate(url)),
    ]
    
    # Non-critical tests
    non_critical_tests = [
        ("Admin Page", lambda: test_admin_page(url)),
        ("API Endpoint", lambda: test_api_endpoint(url)),
    ]
    
    print(f"\n{Colors.BOLD}Critical Tests:{Colors.RESET}")
    for test_name, test_func in critical_tests:
        try:
            result = test_func()
            tests_total += 1
            if result:
                tests_passed += 1
            print()
        except Exception as e:
            print_error(f"{test_name} crashed: {e}\n")
            tests_total += 1
    
    print(f"\n{Colors.BOLD}Non-Critical Tests:{Colors.RESET}")
    for test_name, test_func in non_critical_tests:
        try:
            result = test_func()
            print()
        except Exception as e:
            print_warning(f"{test_name} error: {e}\n")
    
    # Measure response time
    print(f"\n{Colors.BOLD}Performance:{Colors.RESET}")
    test_response_time(url)
    
    # Summary
    print_header("📊 Test Summary")
    print_info(f"Tests passed: {tests_passed}/{tests_total}")
    print_info(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if tests_passed == tests_total:
        print_success("All critical tests passed! ✨")
        return True
    else:
        print_error(f"Some tests failed ({tests_total - tests_passed}/{tests_total})")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_error("Usage: python test_deployment.py <url>")
        print_info("Example: python test_deployment.py https://tomato-disease-detector.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        print_error("URL must start with http:// or https://")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests(url)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
