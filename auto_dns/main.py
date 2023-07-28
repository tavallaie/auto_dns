import os
import yaml
import requests
import typer
from .dns_providers.arvan import Arvan
from .dns_providers import Cloudflare
from .exceptions import UnsupportedProviderError
from tabulate import tabulate


class DNSRecord:
    def __init__(self, domain, record_type, ip, name):
        self.domain = domain
        self.record_type = record_type
        self.ip = ip
        self.name = name


class DDNS:
    def __init__(self, provider):
        self.provider = provider

    def get_record(self, domain, record_type=None, subdomain=None):
        try:

            records = self.provider.get_record(domain, record_type, subdomain)
            if records is None:
                print("No matching records found.")
                return None

            table = []
            for item in records:
                # Make sure 'value' key exists
                if "value" in item:
                    if isinstance(item["value"], list):
                        # Handle case where 'value' is a list of dictionaries
                        for value in item["value"]:
                            table.append(
                                [
                                    item.get("type", "N/A"),
                                    item.get("name", "N/A"),
                                    value.get(
                                        "ip", "N/A"
                                    ),  # always get IP if it is available
                                    item.get("ttl", "N/A"),
                                    item.get("is_protected", "N/A"),
                                ]
                            )
                    elif isinstance(item["value"], dict):
                        # Handle case where 'value' is a dictionary
                        table.append(
                            [
                                item.get("type", "N/A"),
                                item.get("name", "N/A"),
                                item["value"].get(
                                    "host", "N/A"
                                ),  # get host if it is available
                                item.get("ttl", "N/A"),
                                item.get("is_protected", "N/A"),
                            ]
                        )
                    elif isinstance(item["value"], str):
                        # Handle case where 'value' is a string (possible in case of TXT type)
                        table.append(
                            [
                                item.get("type", "N/A"),
                                item.get("name", "N/A"),
                                item[
                                    "value"
                                ],  # directly take the value if it's a string
                                item.get("ttl", "N/A"),
                                item.get("is_protected", "N/A"),
                            ]
                        )

            print(
                tabulate(
                    table,
                    headers=["Type", "Name", "Value", "TTL", "Is Protected"],
                    tablefmt="pretty",
                )
            )
            return records

        except Exception as e:
            print(f"Error getting records: {str(e)}")
            return None

    def create_record(self, record):
        try:
            self.provider.create_record(record)
        except Exception as e:
            print(f"An exception occurred in DDNS create_record: {e}")

    def update_record(self, record):
        try:
            self.provider.update_record(record)
        except Exception as e:
            print(f"An exception occurred in DDNS update_record: {e}")

    def delete_record(self, record):
        try:
            self.provider.delete_record(record)
        except Exception as e:
            print(f"An exception occurred in DDNS delete_record: {e}")


DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".auto_ddns", "config.yaml")


def get_public_ip():
    """Get the public IP address of the device."""
    try:
        response = requests.get("https://api.ipify.org")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as error:
        print(f"Error occurred when getting public IP: {error}")
        raise


def write_config(provider_name: str, api_key: str, config_file: str):
    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file) or {}
    config[provider_name] = {"api_key": api_key}
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w") as file:
        yaml.dump(config, file)


def get_provider(provider_name: str, config_file: str):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    with open(config_file) as file:
        config = yaml.safe_load(file)

    if provider_name == "arvan":
        return Arvan(config["arvan"]["api_key"])
    elif provider_name == "cloudflare":
        return Cloudflare(config["cloudflare"]["api_key"])
    else:
        raise UnsupportedProviderError(f"Unsupported provider: {provider_name}")


app = typer.Typer()


@app.command()
def set_api_key(provider: str, api_key: str, config_file: str = DEFAULT_CONFIG_PATH):
    """Set the API key for a provider."""
    if provider not in ["arvan", "cloudflare"]:
        raise UnsupportedProviderError(f"Unsupported provider: {provider}")
    write_config(provider, api_key, config_file)


@app.command()
def get(
    domain: str,
    provider: str,
    record_type: str = None,
    name: str = None,
    config_file: str = DEFAULT_CONFIG_PATH,
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    ddns.get_record(domain, record_type, name)


@app.command()
def create(
    domain: str,
    record_type: str,
    name: str,
    provider: str,
    ip: str = None,
    config_file: str = DEFAULT_CONFIG_PATH,
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    ip = ip or get_public_ip()
    record = DNSRecord(domain, record_type, ip, name)
    ddns.create_record(record)


@app.command()
def update(
    domain: str,
    name: str,
    record_type: str,
    provider: str,
    ip: str = None,
    config_file: str = DEFAULT_CONFIG_PATH,
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    ip = ip or get_public_ip()
    record = DNSRecord(domain, record_type, ip, name)
    ddns.update_record(record)


@app.command()
def delete(
    domain: str,
    record_type: str,
    name: str,
    provider: str,
    config_file: str = DEFAULT_CONFIG_PATH,
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    record = DNSRecord(
        domain, record_type, "192.168.1.1", name
    )  # placeholder IP for delete operation
    ddns.delete_record(record)


if __name__ == "__main__":
    app()
