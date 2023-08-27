import json
import sys

import requests
from loguru import logger

API_KEY = "YOUR_APT_KEY"


def fetch_owner_details_with_apollo(
    first_name: str, last_name: str, organisation_name: str
) -> dict:
    url = "https://api.apollo.io/v1/people/match"
    headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}
    payload = json.dumps(
        {
            "api_key": API_KEY,
            "first_name": first_name,
            "last_name": last_name,
            "organization_name": organisation_name,
            "reveal_personal_emails": True,
        }
    )

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        logger.error("Apollo API error: " + response.text)
        sys.exit()

    return json.loads(response.text)


def get_owner_details(company_data: dict) -> dict:
    owner_contact_details = {
        "linkedin_url": None,
        "personal_email": None,
        "phone_number": None,
    }
    owner_name = data_from_dict(source=company_data, key_name="owner name")
    organisation_name = data_from_dict(source=company_data, key_name="company name")
    if not (owner_name and organisation_name):
        logger.warning("Cannot find owner details with missing owner basic details")
        return owner_contact_details

    first_name, last_name = get_owner_name_corrected(owner_name=owner_name)
    owner_details_as_dict = fetch_owner_details_with_apollo(
        first_name=first_name, last_name=last_name, organisation_name=organisation_name
    )
    return extract_owner_details(
        details_as_dict=owner_details_as_dict,
        owner_contact_details=owner_contact_details,
    )


def extract_owner_details(details_as_dict: dict, owner_contact_details: dict) -> dict:
    if not isinstance(details_as_dict, dict):
        logger.debug("Source data must be in dict format")
        return owner_contact_details

    person_details = data_from_dict(source=details_as_dict, key_name="person")

    owner_contact_details["linkedin_url"] = data_from_dict(
        source=person_details, key_name="linkedin_url"
    )
    owner_personal_emails = data_from_dict(
        source=person_details, key_name="personal_emails"
    )
    if isinstance(owner_personal_emails, list):
        if len(owner_personal_emails) > 0:
            owner_contact_details["personal_email"] = owner_personal_emails[0]

    owner_phone_numbers = data_from_dict(
        source=person_details, key_name="phone_numbers"
    )
    if isinstance(owner_phone_numbers, list):
        owner_contact_details["phone_number"] = data_from_dict(
            source=owner_phone_numbers[0], key_name="raw_number"
        )
    return owner_contact_details


def get_owner_name_corrected(owner_name: str):
    if " " not in owner_name:
        return owner_name, ""

    owner_name = owner_name.split(" ")
    first_name = owner_name[0]
    last_name = " ".join(owner_name[1:])
    return first_name, last_name


def data_from_dict(source: dict, key_name: str):
    try:
        return source[str(key_name)]
    except KeyError:
        return None
