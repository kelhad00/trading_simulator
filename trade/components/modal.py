import dash_mantine_components as dmc

def modal(id, title, children):
    return dmc.Modal(
        id=id,
        title=dmc.Title(title, order=2, className="font-bold w-full max-w-2xl"),
        overflow="outside",
        className="flex flex-col gap-8",
        padding="xl",
        size="xl",
        radius="md",
        zIndex=10000,
        children=children,
    )