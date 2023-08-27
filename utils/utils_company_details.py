import json
import sys

import requests
from loguru import logger
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from utils.utils_google_page import search_using_query


API_KEY = "YOUR_APT_KEY"


def get_company_domain(driver: Chrome, company_name: str):
    driver = search_using_query(driver=driver, query=company_name)
    try:
        return driver.find_element(By.CLASS_NAME, "Wo6ZAEmESLNUuWBkbMxx").text
    except NoSuchElementException:
        logger.debug("No such company domain found")
        return None


def get_details_using_apollo(domain: str):
    url = "https://api.apollo.io/v1/organizations/enrich"
    headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}
    params = {"api_key": API_KEY, "domain": domain}
    response = requests.get(url=url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error(f"API error: {response.text}")
        sys.exit()

    return json.loads(response.text)


def extract_useful_data(details: dict):
    details = details.get("organization", {})
    return {
        "founded_year": details.get("founded_year", None),
        "estimated_num_employees": details.get("estimated_num_employees", None),
        "industry": details.get("industry"),
        "website_url": details.get("website_url", None),
    }


def get_company_details(driver: Chrome, company_name: str):
    if domain := get_company_domain(driver=driver, company_name=company_name):
        full_details = get_details_using_apollo(domain=domain)
        details = extract_useful_data(details=full_details)
        return details
    return {
        "founded_year": None,
        "estimated_num_employees": None,
        "industry": None,
        "website_url": None,
    }
