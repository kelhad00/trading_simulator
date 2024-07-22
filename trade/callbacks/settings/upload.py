import base64
import os
import dash_mantine_components as dmc

from dash import html, Output, callback, Input, dcc, no_update, State
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.utils.settings.create_market_data import get_generated_data


def upload(contents, filename):
    try:
        if contents is not None:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            save_path = os.path.join(dlt.data_path, filename)

            with open(save_path, 'wb') as f:
                f.write(decoded)

            return dmc.Notification(
                id="notification-upload-charts",
                title="Company added",
                action="show",
                color="green",
                message="File uploaded",
            )

        return no_update

    except Exception as e:
        return dmc.Notification(
            title="Error",
            id="notification-upload-charts",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message="Error while uploading file",
        )  # Feedback si aucun fichier n'est uploadé


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Output('companies', 'data', allow_duplicate=True),
    Input('upload-charts', 'contents'),
    State("companies", "data"),
    prevent_initial_call=True,
)
def upload_charts(contents, companies):
    if contents is None:
        return no_update, no_update

    notif = upload(contents, 'generated_data.csv')

    df = get_generated_data()  # Get the data of all companies
    df_companies = df.columns.get_level_values('symbol').unique()
    intersection = list(set(df_companies) & set(companies))

    for company in intersection:
        companies[company]['got_charts'] = True

    return notif, companies


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Input('upload-news', 'contents'),
    prevent_initial_call=True
)
def upload_news(contents):
    return upload(contents, 'news.csv')


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Input('upload-revenues', 'contents'),
    prevent_initial_call=True
)
def upload_revenues(contents):
    return upload(contents, 'revenues.csv')

