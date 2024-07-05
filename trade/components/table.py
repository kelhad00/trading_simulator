from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify


def create_table(df, id=None):
    columns, values = df.columns, df.values
    header = [
        html.Tr([
            html.Th(col) for col in columns
        ])]
    rows = [html.Tr(
        children=[html.Td(cell) for cell in row],
        id={"type": id, "index": index} if id is not None else "",
        n_clicks=0
    ) for index, row in enumerate(values)]
    table = [
        html.Thead(header),
        html.Tbody(rows)
    ]
    return table

def create_selectable_table(df, id="selectable-table"):
    columns, values = df.columns, df.values
    header = [
        html.Tr(
            [html.Th('')] + [html.Th(col) for col in columns]
        )]

    rows = [
        html.Tr([
            html.Td(
                dmc.Checkbox(
                    checked=False,
                    persistence='session',
                    size='sm',
                    id={'type': id, 'index': index}
                )
            ), *[html.Td(cell) for cell in row]]
        ) for index, row in enumerate(values)]

    table = [html.Thead(header), html.Tbody(rows)]
    return table



def create_table_delete(df, id="table"):
    columns, values = df.columns, df.values
    header = [
        html.Tr(
            [html.Th(col) for col in columns] + [html.Th('')]
        )]

    rows = [
        html.Tr([
            *[html.Td(cell) for cell in row],
            html.Td(
                dmc.ActionIcon(
                    DashIconify(icon="material-symbols:delete-outline", width=20),
                    size="md",
                    radius="md",
                    color="dark",
                    variant="outline",
                    id={"type": id, "index": index},
                    # n_clicks=0,
                ),
            )]
        ) for index, row in enumerate(values)]

    table = [html.Thead(header), html.Tbody(rows)]
    return table