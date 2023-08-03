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
        records = response.json()["data"]

        if record_type:
            print(f"Searching for records of type: {record_type}")
            records = [item for item in records if item["type"] == record_type]

        if subdomain:
            print(f"Searching for records with subdomain: {subdomain}")
            records = [item for item in records if item["name"] == subdomain]

        if not records:
            print("No matching records found.")
            return None

        return records

    def transform_data_to_table(self, records):
        table = []

        for item in records:
            if "value" in item:
                if isinstance(item["value"], list):
                    for value in item["value"]:
                        table.append(
                            [
                                item.get("type", "N/A"),
                                item.get("name", "N/A"),
                                value.get("ip", "N/A"),
                                item.get("ttl", "N/A"),
                                item.get("is_protected", "N/A"),
                            ]
                        )
                elif isinstance(item["value"], dict):
                    table.append(
                        [
                            item.get("type", "N/A"),
                            item.get("name", "N/A"),
                            item["value"].get("host", "N/A"),
                            item.get("ttl", "N/A"),
                            item.get("is_protected", "N/A"),
                        ]
                    )
                elif isinstance(item["value"], str):
                    table.append(
                        [
                            item.get("type", "N/A"),
                            item.get("name", "N/A"),
                            item["value"],
                            item.get("ttl", "N/A"),
                            item.get("is_protected", "N/A"),
                        ]
                    )
        return table

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
