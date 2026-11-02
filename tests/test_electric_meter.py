"""Tests for aioeagle.electric_meter."""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock

import xmltodict

from aioeagle.electric_meter import ElectricMeter


class TestElectricMeter(unittest.IsolatedAsyncioTestCase):
    """Test suite for ElectricMeter."""

    def test_create_instance_without_connection_status(self) -> None:
        """Test create_instance handles missing ConnectionStatus safely."""
        hub = MagicMock()
        hub.make_request = AsyncMock()
        meter = ElectricMeter.create_instance(hub, "0x0013500500123456")

        self.assertEqual(meter.hardware_address, "0x0013500500123456")
        self.assertIsNone(meter.connection_status)
        self.assertFalse(meter.is_connected)

    async def test_empty_device_xml_response(self) -> None:
        """Test get_device_details and get_device_query when EAGLE-3 returns empty <Device></Device>."""
        parsed_empty = xmltodict.parse("<Device></Device>", dict_constructor=dict)
        make_request = AsyncMock(return_value=parsed_empty)
        meter = ElectricMeter(
            {"HardwareAddress": "0x0013500500123456"},
            make_request,
        )

        details = await meter.get_device_details()
        self.assertEqual(details, [])

        query = await meter.get_device_query()
        self.assertEqual(query, {})
        self.assertEqual(meter.hardware_address, "0x0013500500123456")

    async def test_device_query_without_components(self) -> None:
        """Test get_device_query updates DeviceDetails and returns empty dict when Components is omitted."""
        parsed = xmltodict.parse(
            "<Device>"
            "<DeviceDetails>"
            "<HardwareAddress>0x0013500500123456</HardwareAddress>"
            "<ConnectionStatus>Connecting</ConnectionStatus>"
            "</DeviceDetails>"
            "</Device>",
            dict_constructor=dict,
        )
        make_request = AsyncMock(return_value=parsed)
        meter = ElectricMeter(
            {"HardwareAddress": "0x0013500500123456"},
            make_request,
        )

        query = await meter.get_device_query()
        self.assertEqual(query, {})
        self.assertEqual(meter.connection_status, "Connecting")
        self.assertFalse(meter.is_connected)

    async def test_device_query_single_and_multiple_variables(self) -> None:
        """Test get_device_query handles both single Variable dict and multiple Variable list."""
        single_var_xml = (
            "<Device>"
            "<DeviceDetails>"
            "<HardwareAddress>0x0013500500123456</HardwareAddress>"
            "<ConnectionStatus>Connected</ConnectionStatus>"
            "</DeviceDetails>"
            "<Components>"
            "<Component>"
            "<Name>Main</Name>"
            "<Variables>"
            "<Variable><Name>zigbee:InstantaneousDemand</Name><Value>1.234</Value></Variable>"
            "</Variables>"
            "</Component>"
            "</Components>"
            "</Device>"
        )
        make_request = AsyncMock(
            return_value=xmltodict.parse(single_var_xml, dict_constructor=dict)
        )
        meter = ElectricMeter(
            {"HardwareAddress": "0x0013500500123456"},
            make_request,
        )

        result = await meter.get_device_query(["zigbee:InstantaneousDemand"])
        self.assertTrue(meter.is_connected)
        self.assertEqual(
            result["zigbee:InstantaneousDemand"]["Value"],
            "1.234",
        )


if __name__ == "__main__":
    unittest.main()
