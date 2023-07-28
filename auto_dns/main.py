import os
import yaml
import requests
import typer
from auto_dns.dns_providers.arvan import Arvan
from auto_dns.dns_providers.cloudflare import Cloudflare
from auto_dns.exceptions import UnsupportedProviderError


class DNSRecord:
    def __init__(self, domain, record_type, ip):
        self.domain = domain
        self.record_type = record_type
        self.ip = ip


class DDNS:
    def __init__(self, provider):
        self.provider = provider

    def get_record(self, domain, record_type):
        return self.provider.get_record(domain, record_type)

    def create_record(self, record):
        self.provider.create_record(record)

    def update_record(self, record):
        self.provider.update_record(record)

    def delete_record(self, record):
        self.provider.delete_record(record)


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
    domain: str, record_type: str, provider: str, config_file: str = DEFAULT_CONFIG_PATH
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    print(ddns.get_record(domain, record_type))


@app.command()
def create(
    domain: str,
    record_type: str,
    provider: str,
    ip: str = None,
    config_file: str = DEFAULT_CONFIG_PATH,
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    ip = ip or get_public_ip()
    record = DNSRecord(domain, record_type, ip)
    ddns.create_record(record)


@app.command()
def update(
    domain: str,
    record_type: str,
    provider: str,
    ip: str = None,
    config_file: str = DEFAULT_CONFIG_PATH,
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    ip = ip or get_public_ip()
    record = DNSRecord(domain, record_type, ip)
    ddns.update_record(record)


@app.command()
def delete(
    domain: str, record_type: str, provider: str, config_file: str = DEFAULT_CONFIG_PATH
):
    provider_instance = get_provider(provider, config_file)
    ddns = DDNS(provider_instance)
    record = DNSRecord(
        domain, record_type, "192.168.1.1"
    )  # placeholder IP for delete operation
    ddns.delete_record(record)


if __name__ == "__main__":
    app()
