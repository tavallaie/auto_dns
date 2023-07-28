from .base import DNSProvider


class Arvan(DNSProvider):
    base_url = "https://napi.arvancloud.com/cdn/4.0/domains"

    def get_record(self, domain, record_type):
        # Implement Arvan's specific API calls
        pass

    def create_record(self, record):
        # Implement Arvan's specific API calls
        pass

    def update_record(self, record):
        # Implement Arvan's specific API calls
        pass

    def delete_record(self, record):
        # Implement Arvan's specific API calls
        pass
