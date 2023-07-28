import unittest
from unittest.mock import MagicMock, patch
from auto_dns.main import create, update
from auto_dns import __version__
from auto_dns.ddns import DDNS
from auto_dns.dns_providers.base import DNSProvider
from auto_dns.dns_record import DNSRecord


class TestAutoDNS(unittest.TestCase):
    @patch("auto_dns.main.get_provider", return_value=MagicMock(spec=DNSProvider))
    @patch("auto_dns.main.get_public_ip", return_value="192.168.0.1")
    @patch("auto_dns.main.DDNS", return_value=MagicMock(spec=DDNS))
    @patch("auto_dns.main.DNSRecord", return_value=MagicMock(spec=DNSRecord))
    def test_create(
        self, mock_dns_record, mock_ddns, mock_get_public_ip, mock_get_provider
    ):
        # Define test variables
        domain = "example.com"
        record_type = "A"
        name = "test"
        provider = "arvan"
        ip = "192.168.0.1"

        # Call create function
        create(domain, record_type, name, provider, ip)

        # Assert function calls
        mock_get_provider.assert_called_once_with(provider)
        mock_get_public_ip.assert_called_once()
        mock_dns_record.assert_called_once_with(domain, record_type, ip, name)
        mock_ddns.assert_called_once_with(mock_get_provider.return_value)
        mock_ddns.return_value.create_record.assert_called_once_with(
            mock_dns_record.return_value
        )

    @patch("auto_dns.main.get_provider", return_value=MagicMock(spec=DNSProvider))
    @patch("auto_dns.main.get_public_ip", return_value="192.168.0.1")
    @patch("auto_dns.main.DDNS", return_value=MagicMock(spec=DDNS))
    @patch("auto_dns.main.DNSRecord", return_value=MagicMock(spec=DNSRecord))
    def test_update(
        self, mock_dns_record, mock_ddns, mock_get_public_ip, mock_get_provider
    ):
        # Define test variables
        domain = "example.com"
        record_type = "A"
        name = "test"
        provider = "arvan"
        ip = "192.168.0.2"

        # Call update function
        update(domain, name, record_type, provider, ip)

        # Assert function calls
        mock_get_provider.assert_called_once_with(provider)
        mock_get_public_ip.assert_called_once()
        mock_dns_record.assert_called_once_with(domain, record_type, ip, name)
        mock_ddns.assert_called_once_with(mock_get_provider.return_value)
        mock_ddns.return_value.update_record.assert_called_once_with(
            mock_dns_record.return_value
        )

    def test_version(self):
        self.assertEqual(__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
