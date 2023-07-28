from .base import DNSProvider


class Cloudflare(DNSProvider):
    base_url = "https://api.cloudflare.com/client/v4/zones"

    def get_record(self, domain, record_type):
        # Implement Cloudflare's specific API calls
        pass

    def create_record(self, record):
        # Implement Cloudflare's specific API calls
        pass

    def update_record(self, record):
        # Implement Cloudflare's specific API calls
        pass

    def delete_record(self, record):
        # Implement Cloudflare's specific API calls
        pass
