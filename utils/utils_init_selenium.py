from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def initialise_selenium_driver() -> webdriver.Chrome | None:
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    try:
        return webdriver.Chrome(options=chrome_options)
    except Exception:
        logger.error("Driver cannot be initialised")
        return None
