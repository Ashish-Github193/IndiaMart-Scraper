import csv
from contextlib import contextmanager
from random import randint

import pandas as pd
from loguru import logger
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.utils_init_selenium import (
    initialise_selenium_driver,
)


def get_companies_dataframe(path: str):
    try:
        companies = pd.read_csv(path)
        return companies
    except FileNotFoundError:
        logger.error("File not found.")
    except pd.errors.EmptyDataError:
        logger.error("File is empty.")
    except pd.errors.ParserError as e:
        logger.error(f"Error while parsing CSV: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    return None


def wait_for_element_to_load(
    driver: Chrome, by_attr, attr_value: str
) -> WebElement | None:
    try:
        wait = WebDriverWait(driver, 2)
        element = wait.until(EC.presence_of_element_located((by_attr, attr_value)))
        return element
    except TimeoutException:
        logger.critical("Network is very slow")
        return None
    except Exception as e:
        logger.error(e)
        return None


@contextmanager
def managed_selenium_driver():
    driver = initialise_selenium_driver()
    yield driver
    driver.quit()


def get_random_filename(path="./scraped_data/", size=20, extension=".csv"):
    filename = path
    for _ in range(size):
        filename += str(randint(0, 9))
    filename += extension
    return filename


def write_dict_to_csv(file_path, data_dict):
    with open(file_path, "a", newline="\n") as csvfile:
        csv_writer = csv.writer(csvfile)

        if csvfile.tell() == 0:
            header_row = list(data_dict.keys())
            csv_writer.writerow(header_row)
        values_row = list(data_dict.values())
        csv_writer.writerow(values_row)


def close_current_tab_and_switch_to_new_one(driver):
    driver.execute_script("""window.open("","_blank");""")
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def get_all_states_of_india(path):
    states_df = pd.read_csv(path)
    states = states_df['State']
    return list(states)
