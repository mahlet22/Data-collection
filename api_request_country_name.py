import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Initializes headless Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_undp_project_ids(driver, url="https://open.undp.org/projects", limit=5, wait_time=5):
    """Scrapes the UNDP site and returns a list of project IDs."""
    driver.get(url)
    time.sleep(wait_time)  # Wait for dynamic content to load

    project_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/projects/')]")
    
    project_ids = []
    for elem in project_elements:
        href = elem.get_attribute("href")
        if "/projects/" in href:
            project_id = href.split("/projects/")[-1]
            if project_id not in project_ids:
                project_ids.append(project_id)
        if len(project_ids) >= limit:
            break
    return project_ids


def fetch_country_by_project_id(project_id):
    """Fetches country name for a given UNDP project ID using their API."""
    api_url = f"https://api.open.undp.org/api/v1/project/details/{project_id}"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Extract country name from operating_unit.name
        country = data.get("data", {}).get("operating_unit", {}).get("name", "N/A")
        return country
    except requests.RequestException as e:
        print(f"❌ Error fetching data for project {project_id}: {e}")
        return "Error"


def main():
    driver = setup_driver()
    try:
        project_ids = get_undp_project_ids(driver, limit=5)
        print(f"✅ Project IDs found: {project_ids}\n")

        for project_id in project_ids:
            country = fetch_country_by_project_id(project_id)
            print(f"🌍 Project ID: {project_id} → Country: {country}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
