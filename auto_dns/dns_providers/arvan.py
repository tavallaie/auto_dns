import requests
from tabulate import tabulate

API_URL = "https://napi.arvancloud.ir/cdn/4.0/domains/{domain}/dns-records"


class Arvan:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_record(self, domain, record_type=None, name=None):
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
        if name:
            print(f"Searching for records with subdomain: {name}")
            data["data"] = [item for item in data["data"] if item["name"] == name]

        # if no records found, return None
        if not data["data"]:
            print("No matching records found.")
            return None

        return data["data"]

    def create_record(self, record, cloud=False):
        response = requests.post(
            API_URL.format(domain=record.domain),
            headers={"Authorization": f"Apikey {self.api_key}"},
            json={
                "type": record.record_type,
                "value": [
                    {"ip": record.ip, "port": None, "weight": None, "country": None}
                ],
                "name": record.name,
                "ttl": 120,
                "cloud": cloud,
                "upstream_https": "default",
                "ip_filter_mode": {
                    "count": "single",
                    "order": "none",
                    "geo_filter": "none",
                },
            },
        )
        response.raise_for_status()
        return response.json()

    def update_record(self, record, name, cloud=False):
        existing_record = self.get_record(record.domain, record.record_type)
        if existing_record:
            value = {"ip": record.ip, "port": None, "weight": None, "country": None}

            response = requests.put(
                API_URL.format(domain=record.domain) + f"/{existing_record['id']}",
                headers={"Authorization": f"Apikey {self.api_key}"},
                json={
                    "type": record.record_type,
                    "value": [value],
                    "name": name,
                    "ttl": 120,
                    "cloud": cloud,
                    "upstream_https": "default",
                    "ip_filter_mode": {
                        "count": "single",
                        "order": "none",
                        "geo_filter": "none",
                    },
                },
            )
            response.raise_for_status()
            return response.json()
        return None

    def delete_record(self, record):
        existing_records = self.get_record(
            record.domain, record.record_type, record.name
        )
        if existing_records:
            for existing_record in existing_records:
                response = requests.delete(
                    API_URL.format(domain=record.domain) + f"/{existing_record['id']}",
                    headers={"Authorization": f"Apikey {self.api_key}"},
                )
                response.raise_for_status()
        return None
