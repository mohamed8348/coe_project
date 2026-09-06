import os
import json
from typing import Dict, Any

class TestCaseGenerator:
    """Generates executable test cases from bug scenarios."""
    
    def generate_gherkin(self, scenario: Dict[str, Any]) -> str:
        """Generates a proper .feature file content."""
        return f"""Feature: Bug Reproduction - {scenario.get('module', 'Unknown')} Module
  Background:
    Given the ERP system is running version {scenario.get('erp_version', 'latest')}
    And the user is logged in as {scenario.get('reporter_role', 'admin')}

  Scenario: {scenario.get('title', 'Bug Scenario')}
    Given {scenario.get('step1', 'the system is initialized')}
    When {scenario.get('step2', 'an action is performed')}
    Then {scenario.get('expected_result', 'the action succeeds')}
    And the actual behavior is: {scenario.get('actual_result', 'the action fails')}
    # Bug ID: {scenario.get('bug_id', 'BUG-000')}
    # Severity: {scenario.get('severity', 'High')}
"""

    def generate_selenium_script(self, scenario: Dict[str, Any]) -> str:
        """Generates a Python Selenium script."""
        return f"""import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.parametrize('env', ['dev', 'staging'])
def test_bug_{scenario.get('bug_id', '000')}_reproduction(env):
    \"\"\"
    Selenium reproduction for: {scenario.get('title', 'Bug')}
    \"\"\"
    base_url = os.environ.get('ERP_BASE_URL', f'https://{{env}}.erp-system.local')
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate and Login
        driver.get(f"{{base_url}}/login")
        driver.find_element(By.ID, "username").send_keys("{scenario.get('reporter_role', 'admin')}")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "login-btn").click()
        
        # Navigate to module
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-{scenario.get('module', 'home').lower()}"))
        ).click()
        
        # Perform action
        # Given {scenario.get('step1', '')}
        # When {scenario.get('step2', '')}
        
        # Assertions
        # Expected: {scenario.get('expected_result', '')}
        # Actual: {scenario.get('actual_result', '')}
        
        # Dummy assertion to represent the bug check
        # assert "expected state" in driver.page_source, "Bug detected!"
        pass
        
    finally:
        driver.quit()
"""

    def generate_playwright_script(self, scenario: Dict[str, Any]) -> str:
        """Generates a Python Playwright script."""
        return f"""import os
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.parametrize('env', ['dev', 'staging'])
def test_bug_{scenario.get('bug_id', '000')}_reproduction(page: Page, env: str):
    \"\"\"
    Playwright reproduction for: {scenario.get('title', 'Bug')}
    \"\"\"
    base_url = os.environ.get('ERP_BASE_URL', f'https://{{env}}.erp-system.local')
    
    # Login
    page.goto(f"{{base_url}}/login")
    page.fill("#username", "{scenario.get('reporter_role', 'admin')}")
    page.fill("#password", "password123")
    page.click("#login-btn")
    
    # Navigate
    page.click(f"#nav-{scenario.get('module', 'home').lower()}")
    page.screenshot(path="nav_step.png")
    
    # Perform action
    # Given {scenario.get('step1', '')}
    # When {scenario.get('step2', '')}
    
    page.screenshot(path="action_step.png")
    
    # Assertions
    # Expected: {scenario.get('expected_result', '')}
    # Actual: {scenario.get('actual_result', '')}
    
    # expect(page.locator(".status")).to_have_text("expected")
"""

    def generate_postman_collection(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a Postman collection JSON."""
        bug_id = scenario.get('bug_id', '000')
        module = scenario.get('module', 'unknown').lower()
        
        collection = {
            "info": {
                "name": f"Bug {bug_id} Reproduction",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "1. Login",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Content-Type", "value": "application/json"}],
                        "url": {"raw": "{{base_url}}/api/auth/login", "host": ["{{base_url}}"], "path": ["api", "auth", "login"]},
                        "body": {
                            "mode": "raw",
                            "raw": f"{{\\\"username\\\": \\\"{scenario.get('reporter_role', 'admin')}\\\", \\\"password\\\": \\\"password123\\\"}}"
                        }
                    },
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test('Status code is 200', function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});",
                                    "pm.environment.set('token', pm.response.json().token);"
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": f"2. List {module} records",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
                        "url": {"raw": f"{{{{base_url}}}}/api/{module}/records", "host": ["{{base_url}}"], "path": ["api", module, "records"]}
                    }
                },
                {
                    "name": f"3. Perform Action on {module}",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Authorization", "value": "Bearer {{token}}"}, {"key": "Content-Type", "value": "application/json"}],
                        "url": {"raw": f"{{{{base_url}}}}/api/{module}/action", "host": ["{{base_url}}"], "path": ["api", module, "action"]},
                        "body": {
                            "mode": "raw",
                            "raw": "{}"
                        }
                    }
                },
                {
                    "name": f"4. Verify State",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
                        "url": {"raw": f"{{{{base_url}}}}/api/{module}/123", "host": ["{{base_url}}"], "path": ["api", module, "123"]}
                    },
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    f"// Expected: {scenario.get('expected_result', '')}",
                                    f"// Actual bug behavior: {scenario.get('actual_result', '')}",
                                    "pm.test('State verification', function () {",
                                    "    var jsonData = pm.response.json();",
                                    "    // pm.expect(jsonData.state).to.eql('expected');",
                                    "});"
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        return collection

    def save_all(self, scenario: Dict[str, Any], output_dir: str):
        """Saves .feature, .py (selenium), .py (playwright), .json (postman) to output_dir."""
        os.makedirs(output_dir, exist_ok=True)
        bug_id = scenario.get('bug_id', '000')
        
        # 1. Gherkin
        with open(os.path.join(output_dir, f"bug_{bug_id}.feature"), "w") as f:
            f.write(self.generate_gherkin(scenario))
            
        # 2. Selenium
        with open(os.path.join(output_dir, f"test_bug_{bug_id}_selenium.py"), "w") as f:
            f.write(self.generate_selenium_script(scenario))
            
        # 3. Playwright
        with open(os.path.join(output_dir, f"test_bug_{bug_id}_playwright.py"), "w") as f:
            f.write(self.generate_playwright_script(scenario))
            
        # 4. Postman
        with open(os.path.join(output_dir, f"bug_{bug_id}_postman.json"), "w") as f:
            json.dump(self.generate_postman_collection(scenario), f, indent=2)
            
        print(f"Saved generated tests for Bug {bug_id} in {output_dir}")

def main():
    generator = TestCaseGenerator()
    sample_scenario = {
        'module': 'Invoicing',
        'erp_version': 'v14.2',
        'reporter_role': 'FinanceManager',
        'title': 'Invoice approval fails when tax amount is zero',
        'step1': 'an invoice with 0 tax is created',
        'step2': 'the manager clicks approve',
        'expected_result': 'the invoice status changes to APPROVED',
        'actual_result': 'a 500 Server Error is thrown',
        'bug_id': 'INV-4092',
        'severity': 'Critical'
    }
    
    # Save to a local 'out' folder for demonstration
    out_dir = os.path.join(os.path.dirname(__file__), 'output')
    generator.save_all(sample_scenario, out_dir)
    print("Test generation complete.")

if __name__ == '__main__':
    main()
