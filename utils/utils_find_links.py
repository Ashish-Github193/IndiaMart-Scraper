from loguru import logger
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


def get_first_site_link(driver: Chrome):
    refresh_driver_page_source(driver=driver)

    try:
        links = driver.find_elements(By.TAG_NAME, "a")
    except Exception as e:
        logger.warning(e)
        return None

    page_link = "https://www.indiamart.com/"

    try:
        links = [
            link.get_attribute("href")
            for link in links
            if (link.get_attribute("href") and page_link in link.get_attribute("href"))
        ]
        found = links[0]
    except Exception:
        logger.warning("No india mart link found")
        return None

    return found


def refresh_driver_page_source(driver: Chrome):
    return driver.page_source
