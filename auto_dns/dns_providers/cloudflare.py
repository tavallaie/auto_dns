import requests
import json

API_URL = "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"


class Cloudflare:
    ZONES_API = "https://api.cloudflare.com/client/v4/zones"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def get_zone_id(self, domain):
        response = requests.get(
            self.ZONES_API, headers=self.headers, params={"name": domain}
        )
        response.raise_for_status()
        data = response.json()
        if data["result"]:
            return data["result"][0]["id"]
        return None

    def get_record(self, domain, record_type=None, name=None):
        zone_id = self.get_zone_id(domain)
        response = requests.get(API_URL.format(zone_id=zone_id), headers=self.headers)
        response.raise_for_status()
        records = response.json()["result"]

        if record_type:
            print(f"Searching for records of type: {record_type}")
            records = [item for item in records if item["type"] == record_type]

        if name:
            print(f"Searching for records with name: {name}")
            records = [item for item in records if item["name"] == name]

        if not records:
            print("No matching records found.")
            return None

        return records

    # The helper function to transform the data into table format
    def transform_data_to_table(self, records):
        table = []
        for item in records:
            if isinstance(item, dict):  # ensure 'item' is a dictionary
                record_type = item.get("type", "N/A")
                record_name = item.get("name", "N/A")
                record_value = item.get("content", "N/A")  # Updated this line
                record_ttl = item.get("ttl", "N/A")
                record_is_protected = item.get(
                    "proxied", "N/A"
                )  # Cloudflare's proxied status
                table.append(
                    [
                        record_type,
                        record_name,
                        record_value,
                        record_ttl,
                        record_is_protected,
                    ]
                )
        return table

    def create_record(self, record):
        zone_id = self.get_zone_id(record.domain)
        payload = {
            "type": record.record_type,
            "name": record.name,
            "content": record.ip,
            "ttl": 120,
            "proxied": False,
        }

        response = requests.post(
            API_URL.format(zone_id=zone_id), headers=self.headers, json=payload
        )
        response.raise_for_status()
        return response.json()

    def update_record(self, record):
        zone_id = self.get_zone_id(record.domain)
        existing_record = self.get_record(
            record.domain, record.record_type, record.name
        )
        if existing_record:
            payload = {
                "type": record.record_type,
                "name": record.name,
                "content": record.ip,
                "ttl": 120,
                "proxied": False,
            }

            response = requests.put(
                API_URL.format(zone_id=zone_id) + f"/{existing_record[0]['id']}",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

        return None

    def delete_record(self, record):
        zone_id = self.get_zone_id(record.domain)
        existing_records = self.get_record(
            record.domain, record.record_type, record.name
        )
        if existing_records:
            for existing_record in existing_records:
                response = requests.delete(
                    API_URL.format(zone_id=zone_id) + f"/{existing_record['id']}",
                    headers=self.headers,
                )
                response.raise_for_status()
        return None
