import abc


class DNSProvider(abc.ABC):
    def __init__(self, api_key):
        self.api_key = api_key

    @abc.abstractmethod
    def get_record(self, domain, record_type):
        pass

    @abc.abstractmethod
    def create_record(self, record):
        pass

    @abc.abstractmethod
    def update_record(self, record):
        pass

    @abc.abstractmethod
    def delete_record(self, record):
        pass
