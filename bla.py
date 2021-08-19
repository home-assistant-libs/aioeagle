import xmltodict
import dicttoxml

from pprint import pprint
from aioeagle.electric_meter import ElectricMeter

meter = ElectricMeter({"HardwareAddress": "mock hw address"}, None)

components = {
    "Component": {
        "Name": "Main",
        "Variables": [{"Name": var} for var in meter.ENERGY_AND_POWER_VARIABLES],
    }
}

print(
    meter.create_command(
        "device_query", {"Components": components}, {"item_func": lambda _: "Variable"}
    )
)


# pprint(
#     xmltodict.parse(
#         """
# <DeviceList>
# </DeviceList>

# """,
#         dict_constructor=dict,
#     )
# )


# def item_func(parent):
#     print("parent", parent)
#     return "Variable"


# print(
#     dicttoxml.dicttoxml(
#         {
#             "Components": {
#                 "Component": {
#                     "Name": "Main",
#                     "Variables": [
#                         {"Name": "bla"},
#                         {"Name": "bla"},
#                         {"Name": "bla"},
#                         {"Name": "bla"},
#                     ],
#                 }
#             }
#         },
#         root=False,
#         attr_type=False,
#         item_func=item_func,
#     )
# )
