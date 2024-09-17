from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Path to Edge WebDriver executable
edge_driver_path = r"C:\Users\Mayank\Documents\msedgedriver.exe"

# Set up Edge options
edge_options = Options()
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-dev-shm-usage")

# Set up the Edge driver
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service, options=edge_options)

def apply_action_on_driver(action_response: dict):
    actions = action_response.get("action", [])
    for action in actions:
        action_type = action.get("type")
        if action_type == "visit":
            url = action.get("url")
            if url:
                driver.get(url)
        elif action_type == "click":
            xpath = action.get("xpath")
            if xpath:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                element.click()
        elif action_type == "input":
            xpath = action.get("xpath")
            text = action.get("text", "")
            if xpath:
                element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )
                element.clear()
                element.send_keys(text)
