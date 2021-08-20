import asyncio
import sys
from pprint import pprint
import logging

import aiohttp

from aioeagle import EagleHub


logging.basicConfig(level=logging.DEBUG)


async def main():
    async with aiohttp.ClientSession() as session:
        await run(session)


async def run(websession):
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <cloud_id> <install_code> [ip_address]")
        return

    kwargs = {}

    if len(sys.argv) > 3:
        kwargs["host"] = sys.argv[3]

    hub = EagleHub(websession, sys.argv[1], sys.argv[2], **kwargs)

    devices = await hub.get_device_list()

    if len(devices) == 0:
        print("No devices found")
        return

    device = devices[0]

    pprint(device.details)
    print()
    pprint(await device.get_device_query())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
