import sys

import pandas as pd
from loguru import logger
from selenium.webdriver import Chrome

from utils.utils_company_details import get_company_details
from utils.utils_find_links import get_first_site_link
from utils.utils_global import (
    get_companies_dataframe,
    managed_selenium_driver,
    close_current_tab_and_switch_to_new_one,
    get_random_filename,
    write_dict_to_csv, get_all_states_of_india,
)
from utils.utils_google_page import get_google_page
from utils.utils_owner_details import get_owner_details
from utils.utils_website_scraper import Company


def scrape_from_web(driver: Chrome, company: pd.Series, filename: str, states: list):
    link = get_first_site_link(driver=driver)
    if not isinstance(link, str):
        return None

    company_instance = Company(
        driver=driver,
        gstin=company.GSTIN,
        company_name=company.COMPANY_NAME,
        page_link=link,
        states=states
    )
    scraped_data = company_instance.get_scraped_data()
    scraped_data.update(get_owner_details(scraped_data))
    scraped_data.update(
        get_company_details(
            driver=driver, company_name=scraped_data.get("company name")
        )
    )
    logger.info(scraped_data)
    write_dict_to_csv(file_path=filename, data_dict=scraped_data)


def main(input_file_name: str, filename: str, offset: int):
    companies = get_companies_dataframe(path=input_file_name)
    if not isinstance(companies, pd.DataFrame):
        sys.exit()

    with managed_selenium_driver() as driver:
        for index, company in companies.iterrows():
            if int(index) < offset:
                continue

            if get_google_page(driver=driver, company=company):
                states = get_all_states_of_india(path="uploads/states.csv")
                scrape_from_web(driver=driver, company=company, filename=filename, states=states)
                close_current_tab_and_switch_to_new_one(driver)
            else:
                return None


if __name__ == "__main__":
    input_folder_path = "uploads/"
    output_folder_path = "shared/outgoing/"
    input_file = f"{input_folder_path}companies.csv"
    output_file = get_random_filename(
        path=output_folder_path, size=25, extension=".csv"
    )
    main(input_file_name=input_file, filename=output_file, offset=0)
