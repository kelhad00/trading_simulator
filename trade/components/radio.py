import dash_mantine_components as dmc

def radio(options, label, id, value=None):
    return dmc.RadioGroup(
        [dmc.Radio(l, value=k, color="dark") for k, l in options],
        label=label,
        id=id,
        size="sm",
        value=value,
    )