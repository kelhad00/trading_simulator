from dash import html
import dash_mantine_components as dmc

def create_table(df):
    columns, values = df.columns, df.values
    header = [
        html.Tr([
            html.Th(col) for col in columns
        ])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
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