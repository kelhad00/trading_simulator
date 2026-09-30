import base64
import os
import dash_mantine_components as dmc

from dash import Output, callback, Input, no_update, State
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.settings.create_market_data import get_generated_data


def _lang(search):
    return "en" if (search and "lang=en" in search) else "fr"


def upload(contents, filename, lang="fr"):
    """
    Upload a file to the data folder
    """
    tl = tls[lang]["notifications"]
    try:
        if contents is not None:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            save_path = os.path.join(dlt.data_path, filename)

            with open(save_path, 'wb') as f:
                f.write(decoded)

            return dmc.Notification(
                id="notification-upload-charts",
                title=tl["file-uploaded-title"],
                action="show",
                color="green",
                message=tl["file-uploaded"].format(filename=filename),
            )

        return no_update

    except Exception as e:
        return dmc.Notification(
            title=tl["error"],
            id="notification-upload-charts",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message=tl["upload-error"],
        )  # Feedback si aucun fichier n'est uploadé


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Output('companies', 'data', allow_duplicate=True),
    Input('upload-charts', 'contents'),
    State("companies", "data"),
    State("url", "search"),
    prevent_initial_call=True,
)
def upload_charts(contents, companies, search):
    if contents is None:
        return no_update, no_update

    notif = upload(contents, 'generated_data.csv', _lang(search))

    df = get_generated_data()  # Get the data of all companies
    df_companies = df.columns.get_level_values('symbol').unique()  # Get the list of companies in the csv file

    # Get the intersection between the companies in the csv file and the companies in the store
    intersection = list(set(df_companies) & set(companies))
    for company in intersection:
        # Update the got_charts value of the companies in the store
        companies[company]['got_charts'] = True

    return notif, companies


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Input('upload-news', 'contents'),
    State("url", "search"),
    prevent_initial_call=True
)
def upload_news(contents, search):
    return upload(contents, 'news.csv', _lang(search))


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Input('upload-revenues', 'contents'),
    State("url", "search"),
    prevent_initial_call=True
)
def upload_revenues(contents, search):
    return upload(contents, 'revenue.csv', _lang(search))

