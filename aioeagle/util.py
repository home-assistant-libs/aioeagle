from dicttoxml import dicttoxml as dicttoxml_orig


def xmltodict_ensure_list(value, key):
    """Make sure response is a list

    xmltodict doesn't know schema's so doesn't know
    something should be a list or not.
    """
    if value is None:
        return []

    value = value[key]

    if isinstance(value, list):
        return value

    return [value]


def create_command(command, extra_data={}, dicttoxml_args={}):
    """Create a basic command string

    This is used to create a command string that can be used
    to send to the device.
    """
    return dicttoxml(
        {
            "Command": {
                "Name": command,
                **extra_data,
            },
        },
        **dicttoxml_args,
    )


def dicttoxml(value, **kwargs):
    return dicttoxml_orig(value, root=False, attr_type=False, **kwargs)
