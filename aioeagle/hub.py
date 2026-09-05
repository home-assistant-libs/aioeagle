"""EAGLE-200 hub."""

from __future__ import annotations

import asyncio
import logging
import ssl as ssl_lib
from time import time

from aiohttp import ClientSession, encode_basic_auth
import xmltodict

from .electric_meter import ElectricMeter
from .errors import BadAuth
from .util import create_command, xmltodict_ensure_list

_LOGGER = logging.getLogger(__name__)


class EagleHub:
    """EAGLE-200 and EAGLE 3 hub."""

    def __init__(
        self,
        session: ClientSession,
        cloud_id: str,
        install_code: str,
        *,
        host: str | None = None,
        protocol: str = "http",
        port: int | None = None,
        ssl: bool | ssl_lib.SSLContext | None = None,
    ) -> None:
        """Initialize hub."""
        self.session = session
        if host is None:
            self.host = f"eagle-{cloud_id}.local"
        else:
            self.host = host
        self.cloud_id = cloud_id
        self.install_code = install_code
        self.protocol = protocol
        self.port = port or (443 if protocol == "https" else 80)
        self.ssl = ssl
        self.devices = []
        self.auth_header = encode_basic_auth(cloud_id, install_code)
        self.next_request = time()

    async def make_request(self, command_xml: str):
        """Make a request."""
        wait_time = self.next_request - time()
        if wait_time > 0:
            _LOGGER.debug("Sleeping %s", wait_time)
            await asyncio.sleep(wait_time)

        port_suffix = (
            f":{self.port}"
            if (self.protocol == "http" and self.port != 80)
            or (self.protocol == "https" and self.port != 443)
            else ""
        )
        url = f"{self.protocol}://{self.host}{port_suffix}/cgi-bin/post_manager"
        _LOGGER.debug("Sending to %s: %s", url, command_xml)

        post_kwargs = {
            "headers": {
                "Authorization": self.auth_header,
                "content-type": "text/xml",
            },
            "data": command_xml,
        }
        if self.ssl is not None:
            post_kwargs["ssl"] = self.ssl

        async with self.session.post(url, **post_kwargs) as response:
            # Wait a second until the next request
            self.next_request = time() + 1

            if response.status == 401:
                raise BadAuth

            text = await response.text()
            return xmltodict.parse(text, dict_constructor=dict)

    async def get_device_list(self) -> list[ElectricMeter]:
        """Get a list of devices."""
        response = await self.make_request(create_command("device_list"))
        result = []

        for device in xmltodict_ensure_list(response["DeviceList"], "Device"):
            if device["ModelId"] == "electric_meter":
                result.append(ElectricMeter(device, self.make_request))
            else:
                _LOGGER.debug(f"Skipping unknown device {device['ModelId']}")

        return result
