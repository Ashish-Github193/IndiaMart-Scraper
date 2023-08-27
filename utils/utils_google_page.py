import pandas as pd
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_google_page(driver: webdriver.Chrome, company: pd.Series):
    search_query = create_search_query(company=company)
    if not isinstance(search_query, str):
        return None

    logger.info(f"Search query: '{search_query}'.")
    driver = search_using_query(driver=driver, query=search_query)
    if not isinstance(driver, webdriver.Chrome):
        return None

    return driver


def create_search_query(company: pd.Series):
    try:
        return f"{company.GSTIN} {company.COMPANY_NAME} site:indiamart.com"
    except AttributeError as A:
        logger.error(f"Missing column name '{A}'")
        return None
    except Exception as E:
        logger.error(f"{E}")
        return None


def search_using_query(driver: webdriver.Chrome, query: str):
    try:
        driver.get("https://duckduckgo.com/")
        element = driver.find_element(By.NAME, "q")
        element.send_keys(query)
        element.send_keys(Keys.ENTER)
    except Exception:
        logger.error("Driver failed to search the query")
        return None

    return driver
