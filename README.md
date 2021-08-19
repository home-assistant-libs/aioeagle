# Aioeagle

## Asynchronous library to control Rainforest EAGLE-200

Requires Python 3.8+ and uses asyncio and aiohttp.

```python
import asyncio
from pprint import pprint

import aiohttp
from aioeagle.discovery import discover_nupnp


CLOUD_ID = "123456"
INSTALL_CODE = "abcdefghijklmn"


async def main():
    async with aiohttp.ClientSession() as session:
        await run(session)


async def run(websession):
    hub = EagleHub(websession, CLOUD_ID, INSTALL_CODE)
    devices = await hub.get_device_list()

    if len(devices) == 0:
        print("No devices found")
        return

    device = devices[0]

    pprint(device.details)
    print()
    pprint(await device.get_device_query(device.ENERGY_AND_POWER_VARIABLES))


asyncio.run(main())
```

## Timeouts

Aioeagle does not specify any timeouts for any requests. You will need to specify them in your own code. We recommend the `async_timeout` package:

```python
import async_timeout

with async_timeout.timeout(10):
    await bridge.initialize()
```

## Contribution guidelines

Object hierarchy and property/method names should match the EAGLE-200 API.
