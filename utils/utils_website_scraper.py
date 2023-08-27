from typing import Dict, List
import re

from loguru import logger
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from utils.utils_global import wait_for_element_to_load


class Company:
    def __init__(
        self, driver: Chrome, gstin: str, company_name: str, page_link: str, states: list
    ) -> None:
        self.driver = driver
        self.gstin = gstin
        self.company_name = company_name
        self.page_link = page_link
        self.address = None
        self.owner = None
        self.phone = None
        self.products = {}
        self.nature_of_business = None
        self.annual_turnover = None
        self.state = None
        self.zip_code = None

        self.start_scraping(states=states)

    def get_scraped_data(self) -> Dict:
        return {
            "gstin": self.gstin,
            "company name": self.company_name,
            "page link": self.page_link,
            "address": self.address,
            "state": self.state,
            "zip code": self.zip_code,
            "owner name": self.owner,
            "phone number": self.phone,
            "products": self.products,
            "nature of business": self.nature_of_business,
            "annual turnover": self.annual_turnover,
        }

    def start_scraping(self, states: list):
        self.scrape_contact_us()
        self.scrape_owner_name()
        self.scrape_mobile_number()
        self.scrape_products_data()
        self.scrape_basic_data()
        self.get_state_name(states)
        self.get_zip_code()

    def scrape_contact_us(self):
        self.driver.get(self.page_link)
        element = wait_for_element_to_load(
            driver=self.driver,
            by_attr=By.CSS_SELECTOR,
            attr_value="ul[class='FM_ds5 FM_f16 FM_w1']",
        )
        if element is None:
            logger.debug("Company data not found")
            return None

        contact_us_btn_xpath = "//a[contains(text(), 'Contact Us')]"
        try:
            self.driver.find_element(By.XPATH, contact_us_btn_xpath).click()
        except NoSuchElementException:
            logger.debug("'Contact us' element not found")
            return None

        self.get_address()

    def get_address(self):
        element_class = "FM_Lsp4 FM_C0 Fm_lh22"
        try:
            address = self.driver.find_element(
                By.CSS_SELECTOR, f"p[class='{element_class}']"
            )
        except NoSuchElementException:
            logger.debug("'Address' element not found")
            return None

        address = address.get_attribute("innerHTML").strip()
        self.address = address[: address.index("<")] if ("<" in address) else address

    def get_state_name(self, states: list[str]):
        if self.address is not None:
            preprocessed_address = self.address.split(',')
            preprocessed_address = preprocessed_address[-2]
            preprocessed_address = preprocess_string(preprocessed_address)
            threshold = 0.4
            for state in states:
                preprocessed_state = preprocess_string(state)
                if find_string_b_in_string_a(string_a=preprocessed_address, string_b=preprocessed_state,
                                             threshold=threshold):
                    self.state = state.lower()
                    break

    def get_zip_code(self):
        if self.address is not None:
            zip_code_pattern = r'\b\d{6}\b'
            if match := re.search(zip_code_pattern, self.address):
                self.zip_code = match.group()

    def scrape_owner_name(self):
        element_class = "FM_Lsp4 FM_f15 FM_c7 FM_p29"
        try:
            owner_name_element = self.driver.find_element(
                By.CSS_SELECTOR, f"p[class='{element_class}']"
            )
        except NoSuchElementException:
            logger.debug("'Owner Name' element not found")
            return None

        self.owner = owner_name_element.get_attribute("innerHTML").strip()

    def scrape_mobile_number(self):
        try:
            call_btn = self.driver.find_element(By.ID, "footerPNS")
            self.phone = call_btn.get_attribute("data-pnsno")
        except NoSuchElementException:
            logger.debug("'Mobile Number' element not found")
            return None
        except Exception as e:
            logger.debug(e)
            return None

    def scrape_products_data(self):
        products = scrape_products_and_range_data(driver=self.driver)
        if not isinstance(products, list):
            return None

        for data_as_dict in convert_products_to_dict(products=products):
            if not (isinstance(data_as_dict, dict)):
                return None

            self.products.update(data_as_dict)

    def scrape_basic_data(self):
        if navigate_to_home(driver=self.driver):
            self.nature_of_business = scrape_nature_of_business(driver=self.driver)
            self.annual_turnover = scrape_annual_turnover(driver=self.driver)


def scrape_products_and_range_data(driver: Chrome):
    selector = "div.ddnav.FM_pa.zx1.FM_ps_l.FM_ds6.FM_bs.FM_ds5"
    try:
        products_and_range = driver.find_element(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        logger.debug("'Products and Range' element not found")
        return None

    try:
        child_elements = products_and_range.find_elements(
            By.XPATH, ".//li[@class='FM_f16 FM_bo']"
        )
    except NoSuchElementException:
        logger.debug("No products found")
        return None

    return child_elements


def convert_products_to_dict(
    products: list[WebElement],
) -> Dict[str, List[str] | str] | None:
    for product in products:
        try:
            product_name = product.find_element(By.TAG_NAME, "a").get_attribute(
                "innerHTML"
            )
        except NoSuchElementException:
            return None
        sub_products = scrape_sub_product_names(product=product)
        data = {product_name: sub_products}
        yield data
    return None


def scrape_sub_product_names(product: WebElement):
    try:
        child_list_items = product.find_elements(
            By.XPATH, ".//a[@class='Fm_lh17 FM_Db']"
        )
        return [
            sub_product.get_attribute("innerHTML") for sub_product in child_list_items
        ]
    except NoSuchElementException:
        return []


def navigate_to_home(driver: Chrome) -> bool:
    xpath = (
        "//a[contains(text(), 'Home') and (@href='./' or @href='javascript:void(0);')]"
    )
    try:
        driver.find_element(By.XPATH, xpath).click()
        return True
    except NoSuchElementException:
        logger.debug("'Home' element not found")
        return False
    except Exception as e:
        logger.debug(f"Unable to locate home: '{e}'")
        return False

def scrape_nature_of_business(driver: Chrome):
    xpath1 = "//p[contains(text(), 'Nature of Business')]"
    xpath2 = "following-sibling::span[1]"
    try:
        element = driver.find_element(By.XPATH, xpath1)
        nature_of_business = element.find_element(By.XPATH, xpath2)
        return nature_of_business.get_attribute("innerHTML")
    except NoSuchElementException:
        logger.debug("'Nature of Business' Element not found")
        return None


def scrape_annual_turnover(driver: Chrome):
    xpath1 = "//p[contains(text(), 'Annual Turnover')]"
    xpath2 = "following-sibling::span[1]"
    try:
        element = driver.find_element(By.XPATH, xpath1)
        annual_turnover = element.find_element(By.XPATH, xpath2)
        return annual_turnover.get_attribute("innerHTML")
    except NoSuchElementException:
        logger.debug("'Annual Turnover' Element not found")
        return None


def preprocess_string(input_string):
    return re.sub(r'[^\w\s]', '', input_string).lower()


def jaccard_similarity(str_a, str_b):
    set_a = set(str_a.split())
    set_b = set(str_b.split())
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union


def find_string_b_in_string_a(string_a, string_b, threshold=0.7):
    processed_a = preprocess_string(string_a)
    processed_b = preprocess_string(string_b)
    similarity_score = jaccard_similarity(processed_a, processed_b)
    return similarity_score >= threshold
