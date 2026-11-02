from .util import xmltodict_ensure_list, create_command


class ElectricMeter:
    """Represent an electric meter.

    {'ConnectionStatus': 'Connected',
      'HardwareAddress': '0x00abcd123',
      'LastContact': '0x611d885a',
      'Manufacturer': 'Generic',
      'ModelId': 'electric_meter',
      'Name': 'Power Meter',
      'NetworkAddress': '0x0000',
      'Protocol': 'Zigbee'}
    """

    # Bug in the API is causing CurrentSummationDelivered not
    # to be returned. So just fetch all (default behavior)
    ENERGY_AND_POWER_VARIABLES = [
        "zigbee:InstantaneousDemand",
        "zigbee:CurrentSummationDelivered",
        "zigbee:CurrentSummationReceived",
    ]

    @classmethod
    def create_instance(cls, hub, hardware_address):
        """Create a new electric meter."""
        return cls(
            {
                "HardwareAddress": hardware_address,
            },
            hub.make_request,
        )

    def __init__(self, details, make_request):
        """Initialize the electric meter."""
        self.details = details
        self.make_request = make_request

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return (self.details or {}).get("ConnectionStatus") == "Connected"

    @property
    def connection_status(self) -> str | None:
        return (self.details or {}).get("ConnectionStatus")

    @property
    def hardware_address(self) -> str | None:
        return (self.details or {}).get("HardwareAddress")

    @property
    def last_contact(self) -> str | None:
        return (self.details or {}).get("LastContact")

    @property
    def manufacturer(self) -> str | None:
        return (self.details or {}).get("Manufacturer")

    @property
    def model_id(self) -> str | None:
        return (self.details or {}).get("ModelId")

    @property
    def name(self) -> str | None:
        return (self.details or {}).get("Name")

    @property
    def network_address(self) -> str | None:
        return (self.details or {}).get("NetworkAddress")

    @property
    def protocol(self) -> str | None:
        return (self.details or {}).get("Protocol")

    def create_command(self, command, extra_data={}):
        """Create command targeting this device."""
        return create_command(
            command,
            {"DeviceDetails": {"HardwareAddress": self.hardware_address}, **extra_data},
        )

    async def get_device_details(self):
        data = await self.make_request(
            self.create_command(
                "device_details",
            )
        )
        dev = (data or {}).get("Device") or {}
        if "Components" not in dev or not dev["Components"]:
            return []
        return xmltodict_ensure_list(dev["Components"], "Component")

    async def get_device_query(self, variables=None):
        """Query data."""
        if variables is None:
            components = {"All": "Y"}
        else:
            components = {
                "Component": {
                    "Name": "Main",
                    "Variables": [{"Variable": {"Name": var}} for var in variables],
                }
            }
        data = await self.make_request(
            self.create_command(
                "device_query",
                {"Components": components},
            )
        )
        dev = (data or {}).get("Device") or {}
        if isinstance(dev.get("DeviceDetails"), dict):
            self.details = {**(self.details or {}), **dev["DeviceDetails"]}

        result = {}
        if "Components" not in dev or not dev["Components"]:
            return result
        for component in xmltodict_ensure_list(dev["Components"], "Component"):
            for variable in xmltodict_ensure_list(
                (component or {}).get("Variables"), "Variable"
            ):
                result[variable["Name"]] = variable

        return result

    def __repr__(self) -> str:
        return f"<ElectricMeter {(self.details or {}).get('Name', '')}>"
