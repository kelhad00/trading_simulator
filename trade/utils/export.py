from uuid import uuid4
import ast

import pandas as pd
from datetime import datetime
import os
from dash import page_registry

from trade.defaults import defaults as dlt
from trade.locales import translations as tls


def format_portfolio_dataframe(df, name):
    try:
        df = pd.DataFrame.from_dict(df, orient='index').T
        columns = dict(zip(df.columns, [col + name for col in df.columns]))
        df.rename(columns=columns, inplace=True)
        return df
    except:
        return pd.DataFrame()

def format_requests_dataframe(request_list, max_requests):
    try:
        new_columns_data = {}
        df = pd.DataFrame(request_list, columns=['action', 'shares', 'company', 'price']).T
        for i in range(0, max_requests):  # Parcourir les 10 actions (de 1 à 10)
            action_col_name = f"request-{i+1}"
            try:
                action_data = df[i]  # Extraire les données pour l'action i
                new_columns_data[action_col_name] = f"{action_data['action']} {action_data['price']} {action_data['shares']} {action_data['company']}"
            except:
                new_columns_data[action_col_name] = None

        return pd.DataFrame.from_dict(new_columns_data, orient="index").T
    except:
        return pd.DataFrame()



def format_charts_type(chart_type):
    lang = page_registry['lang']
    if chart_type == tls[lang]['tab-market']:
        return "market"
    else:
        return "revenue"


def format_deleted_requests(deleted_request):
    if deleted_request is None:
        deleted_request = []
    else:
        deleted_request = list(deleted_request)
    return deleted_request


def get_last_visible_curves():
    """Récupère l'état des courbes visibles de la dernière entrée dans les logs"""
    default_curves = ['longMA', 'shortMA', 'twohunMA', 'RSI']
    file_path = os.path.join(dlt.data_path, 'export', 'interface-logs.csv')
    
    try:
        if not os.path.exists(file_path):
            return default_curves

        # Lire uniquement la dernière ligne du fichier
        with open(file_path, 'rb') as f:
            # Aller à la fin du fichier
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            
            # Si le fichier est vide
            if file_size == 0:
                return default_curves
                
            # Remonter depuis la fin pour trouver la dernière ligne complète
            pos = file_size - 1
            while pos > 0 and f.read(1) != b'\n':
                pos -= 1
                f.seek(pos, os.SEEK_SET)
            
            # Lire la dernière ligne
            last_line = f.readline().decode()
            
            # Si la ligne est vide
            if not last_line.strip():
                return default_curves
            
            # Parser la dernière ligne comme CSV
            columns = pd.read_csv(file_path, nrows=0).columns
            last_row = pd.read_csv(pd.io.common.StringIO(last_line), names=columns)
            
            # Récupérer la valeur des courbes visibles
            curves_str = last_row['visible_curves'].iloc[0]
            if pd.isna(curves_str):
                return default_curves
                
            # Utiliser ast.literal_eval pour une conversion sûre de la chaîne en liste
            curves = ast.literal_eval(curves_str)
            return curves if isinstance(curves, list) else default_curves
            
    except Exception as e:
        print("Error reading last visible curves:", str(e))
        return default_curves


def export_data(
        timestamp,
        request_list,
        cashflow,
        shares,
        totals,
        company_id,
        news_title,
        graph_type,  # used to know which type of charts is displayed
        form_type,  # used to know if user is going to buy or sell
        deleted_request=None,
        trigger=None,
        restyle_data=None,
        max_requests=dlt.max_requests
):
    """ Periodically save state of the trade into csv
    """

    deleted_request = format_deleted_requests(deleted_request)
    charts = format_charts_type(graph_type)
    requests = format_requests_dataframe(request_list, max_requests)
    shares = format_portfolio_dataframe(shares, "-shares")
    totals = format_portfolio_dataframe(totals, "-totals")

    # generate an uuid
    uuid = str(uuid4())

    # Récupérer l'état des courbes depuis le dernier log
    visible_curves = get_last_visible_curves()
    
    if trigger == 'company-graph' and restyle_data is not None:
        try:

            
            # restyle_data est une liste contenant les modifications de style
            # Le premier élément contient les changements de visibilité
            # Le second élément contient les indices des traces modifiées
            style_update, trace_indices = restyle_data
            

            # Si 'visible' est dans les mises à jour de style
            if 'visible' in style_update:
                visibility = style_update['visible'][0]
                
                # Pour chaque trace modifiée
                for idx in trace_indices:
                    # Mapping des indices vers les noms des courbes
                    # 0: longMA, 1: shortMA, 2: twohunMA, 3: candlestick (toujours visible), 4: RSI
                    if idx == 0 and 'longMA' in visible_curves and  visibility == "legendonly":
                        visible_curves.remove('longMA')
                    elif idx == 1 and 'shortMA' in visible_curves and  visibility == "legendonly":
                        visible_curves.remove('shortMA')
                    elif idx == 2 and 'twohunMA' in visible_curves and  visibility == "legendonly":
                        visible_curves.remove('twohunMA')
                    elif idx == 4 and 'RSI' in visible_curves and visibility == "legendonly":
                        visible_curves.remove('RSI')
                    elif visibility:  # Si on réactive une courbe
                        if idx == 0 and 'longMA' not in visible_curves:
                            visible_curves.append('longMA')
                        elif idx == 1 and 'shortMA' not in visible_curves:
                            visible_curves.append('shortMA')
                        elif idx == 2 and 'twohunMA' not in visible_curves:
                            visible_curves.append('twohunMA')
                        elif idx == 4 and 'RSI' not in visible_curves:
                            visible_curves.append('RSI')

        except Exception as e:
            # En cas d'erreur, on garde l'état précédent
            pass

    df = pd.DataFrame({
        "uuid": [uuid],
        "market-timestamp": [timestamp],
        "host-timestamp": [datetime.now().timestamp()],
        "cashflow": [cashflow],
        "selected-company": [company_id],
        "form-action": [form_type],
        "chart-type": [charts],
        "is_news_description_displayed": [False if news_title is None else True],
        "news_title": [news_title],
        "visible_curves": [str(visible_curves)]  # On enregistre toujours la liste des courbes visibles
    })

    portfolio_df = pd.DataFrame({"uuid": [uuid]})
    portfolio_df = portfolio_df.merge(shares, how='left', left_index=True, right_index=True)
    portfolio_df = portfolio_df.merge(totals, how='left', left_index=True, right_index=True)

    request_df = pd.DataFrame({"uuid": [uuid], "deleted-request": [deleted_request]})
    request_df = request_df.merge(requests, how='left', left_index=True, right_index=True)

    # Save the header only once and append the rest
    file_path = os.path.join(dlt.data_path, 'export', 'interface-logs.csv')
    portfolio_path = os.path.join(dlt.data_path, 'export', 'portfolio-logs.csv')
    request_path = os.path.join(dlt.data_path, 'export', 'request-logs.csv')

    save_df(df, file_path)
    save_df(portfolio_df, portfolio_path)
    save_df(request_df, request_path)


def save_df(df, file_path):
    if os.path.isfile(file_path):
        df.to_csv(file_path, mode='a', index=False, header=False)
    else:
        df.to_csv(file_path, index=False)
