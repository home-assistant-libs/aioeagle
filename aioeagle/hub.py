"""EAGLE-200 hub."""
from __future__ import annotations

import asyncio
import logging
from time import time

from aiohttp import ClientSession, BasicAuth
import xmltodict

from .electric_meter import ElectricMeter
from .errors import BadAuth
from .util import create_command, xmltodict_ensure_list

_LOGGER = logging.getLogger(__name__)


class EagleHub:
    """EAGLE-200 hub."""

    def __init__(
        self,
        session: ClientSession,
        cloud_id: str,
        install_code: str,
        *,
        host: str | None = None,
    ) -> None:
        """Initialize hub."""
        self.session = session
        if host is None:
            self.host = f"eagle-{cloud_id}.local"
        else:
            self.host = host
        self.cloud_id = cloud_id
        self.install_code = install_code
        self.devices = []
        self.auth = BasicAuth(cloud_id, install_code)
        self.next_request = time()

    async def make_request(self, command_xml: str):
        """Make a request."""
        wait_time = self.next_request - time()
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        async with self.session.post(
            f"http://{self.host}/cgi-bin/post_manager",
            auth=self.auth,
            headers={"content-type": "text/xml"},
            data=command_xml,
        ) as response:
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
