import dash
from trade.layouts.settings.layout import main_layout_settings

# Don't delete this import
from trade.callbacks.settings import stocks, advanced, news, upload, revenues
from trade.callbacks.settings.charts import charts, modal

dash.register_page(__name__, path="/settings",)


def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang
    return main_layout_settings(lang)