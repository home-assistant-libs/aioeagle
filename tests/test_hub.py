"""Tests for aioeagle.hub."""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock

from aioeagle.errors import BadAuth
from aioeagle.hub import EagleHub


class TestEagleHub(unittest.IsolatedAsyncioTestCase):
    """Test suite for EagleHub."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.cloud_id = "abcdef"
        self.install_code = "0123456789abcdef"

    def test_default_init(self):
        """Test default initialization for Eagle-200."""
        hub = EagleHub(self.mock_session, self.cloud_id, self.install_code)

        self.assertEqual(hub.host, "eagle-abcdef.local")
        self.assertEqual(hub.protocol, "http")
        self.assertEqual(hub.port, 80)
        self.assertIsNone(hub.ssl)

    def test_init_with_custom_host(self):
        """Test initialization with explicit host."""
        hub = EagleHub(
            self.mock_session,
            self.cloud_id,
            self.install_code,
            host="192.168.1.50",
        )

        self.assertEqual(hub.host, "192.168.1.50")
        self.assertEqual(hub.protocol, "http")
        self.assertEqual(hub.port, 80)

    def test_init_for_eagle_3_https(self):
        """Test initialization for Eagle 3 with HTTPS and disabled SSL check."""
        hub = EagleHub(
            self.mock_session,
            self.cloud_id,
            self.install_code,
            host="192.168.1.51",
            protocol="https",
            ssl=False,
        )

        self.assertEqual(hub.host, "192.168.1.51")
        self.assertEqual(hub.protocol, "https")
        self.assertEqual(hub.port, 443)
        self.assertFalse(hub.ssl)

    def test_init_with_custom_port(self):
        """Test initialization with custom port."""
        hub = EagleHub(
            self.mock_session,
            self.cloud_id,
            self.install_code,
            host="192.168.1.50",
            protocol="https",
            port=8443,
            ssl=False,
        )

        self.assertEqual(hub.port, 8443)
        self.assertEqual(hub.protocol, "https")

    async def test_make_request_http_default(self):
        """Test make_request generates correct default HTTP request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<DeviceList><Device><ModelId>electric_meter</ModelId></Device></DeviceList>"

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        self.mock_session.post.return_value = mock_post_context

        hub = EagleHub(
            self.mock_session,
            self.cloud_id,
            self.install_code,
            host="192.168.1.50",
        )

        result = await hub.make_request("<Command>test</Command>")

        self.mock_session.post.assert_called_once()
        call_args, call_kwargs = self.mock_session.post.call_args

        self.assertEqual(call_args[0], "http://192.168.1.50/cgi-bin/post_manager")
        self.assertNotIn("ssl", call_kwargs)
        self.assertIn("DeviceList", result)

    async def test_make_request_https_eagle_3(self):
        """Test make_request generates correct HTTPS request with ssl=False."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<DeviceList></DeviceList>"

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        self.mock_session.post.return_value = mock_post_context

        hub = EagleHub(
            self.mock_session,
            self.cloud_id,
            self.install_code,
            host="192.168.1.51",
            protocol="https",
            ssl=False,
        )

        result = await hub.make_request("<Command>test</Command>")

        self.mock_session.post.assert_called_once()
        call_args, call_kwargs = self.mock_session.post.call_args

        self.assertEqual(call_args[0], "https://192.168.1.51/cgi-bin/post_manager")
        self.assertIn("ssl", call_kwargs)
        self.assertFalse(call_kwargs["ssl"])
        self.assertIn("DeviceList", result)

    async def test_make_request_custom_port(self):
        """Test make_request includes port when non-standard."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<DeviceList></DeviceList>"

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        self.mock_session.post.return_value = mock_post_context

        hub = EagleHub(
            self.mock_session,
            self.cloud_id,
            self.install_code,
            host="192.168.1.51",
            protocol="https",
            port=8443,
            ssl=False,
        )

        await hub.make_request("<Command>test</Command>")

        call_args, _ = self.mock_session.post.call_args
        self.assertEqual(call_args[0], "https://192.168.1.51:8443/cgi-bin/post_manager")

    async def test_make_request_bad_auth(self):
        """Test make_request raises BadAuth on 401."""
        mock_response = AsyncMock()
        mock_response.status = 401

        mock_post_context = AsyncMock()
        mock_post_context.__aenter__.return_value = mock_response
        self.mock_session.post.return_value = mock_post_context

        hub = EagleHub(
            self.mock_session,
            self.cloud_id,
            self.install_code,
            host="192.168.1.50",
        )

        with self.assertRaises(BadAuth):
            await hub.make_request("<Command>test</Command>")


if __name__ == "__main__":
    unittest.main()
