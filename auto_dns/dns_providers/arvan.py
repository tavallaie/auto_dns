import requests
from tabulate import tabulate

API_URL = "https://napi.arvancloud.ir/cdn/4.0/domains/{domain}/dns-records"


class Arvan:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_record(self, domain, record_type=None, subdomain=None):
        response = requests.get(
            API_URL.format(domain=domain),
            headers={"Authorization": f"Apikey {self.api_key}"},
        )
        response.raise_for_status()
        data = response.json()

        # if record_type is provided, filter by type
        if record_type:
            print(f"Searching for records of type: {record_type}")
            data["data"] = [
                item for item in data["data"] if item["type"] == record_type
            ]

        # if subdomain is provided, filter by name
        if subdomain:
            print(f"Searching for records with subdomain: {subdomain}")
            data["data"] = [item for item in data["data"] if item["name"] == subdomain]

        # if no records found, return None
        if not data["data"]:
            print("No matching records found.")
            return None

        return data["data"]

    def create_record(self, record):
        response = requests.post(
            API_URL.format(domain=record.domain),
            headers={"Authorization": f"Apikey {self.api_key}"},
            json={
                "type": record.record_type,
                "value": record.ip,
                "name": "",
            },
        )
        response.raise_for_status()
        return response.json()

    def update_record(self, record):
        existing_record = self.get_record(record.domain, record.record_type)
        if existing_record:
            response = requests.put(
                API_URL.format(domain=record.domain) + f"/{existing_record['id']}",
                headers={"Authorization": f"Apikey {self.api_key}"},
                json={
                    "type": record.record_type,
                    "value": record.ip,
                    "name": "",
                },
            )
            response.raise_for_status()
            return response.json()
        return None

    def delete_record(self, record):
        existing_record = self.get_record(record.domain, record.record_type)
        if existing_record:
            response = requests.delete(
                API_URL.format(domain=record.domain) + f"/{existing_record['id']}",
                headers={"Authorization": f"Apikey {self.api_key}"},
            )
            response.raise_for_status()
            return response.json()
        return None
