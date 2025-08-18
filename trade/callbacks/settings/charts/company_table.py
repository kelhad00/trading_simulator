from dash import callback, Input, Output, html, page_registry
import dash_mantine_components as dmc


def parse_size_data_for_tooltip(size_data):
    """Parse size data to extract trends for tooltip display"""
    if not size_data:
        return "Aucune tendance configurée"
    
    trends = []
    for item in size_data:
        item_data = size_data[item]
        if item_data.get("width", 0) > 0:
            label = item_data.get("label", "")
            if label:
                trends.append(label)
    
    if not trends:
        return "Aucune tendance configurée"
    
    return "Tendances : " + ", ".join(trends)


@callback(
    Output("companies-config-table", "children"),
    Input("companies", "data"),
    Input("company-configs", "data"),
)
def render_companies_config_table(companies, company_configs):
    if not companies:
        return dmc.Text("Aucune compagnie", size="sm")

    # Build table rows
    rows = []
    company_configs = company_configs or {}
    for ticker, info in companies.items():
        configured = ticker in company_configs
        
        if configured:
            # Extract trends for tooltip
            size_data = company_configs[ticker].get("size_data", {})
            tooltip_text = parse_size_data_for_tooltip(size_data)
            
            badge = dmc.Tooltip(
                label=tooltip_text,
                children=dmc.Badge(
                    "Configuré",
                    color="green",
                    variant="light",
                    radius="xs",
                ),
                position="top",
                withArrow=True,
                multiline=True,
                width=300,
                styles={"tooltip": {"textAlign": "left"}}
            )
        else:
            badge = dmc.Badge(
                "Non configuré",
                color="red",
                variant="light",
                radius="xs",
            )
        
        rows.append(
            html.Tr([
                html.Td(dmc.Text(ticker, size="sm")),
                html.Td(badge, style={"textAlign": "right", "display": "flex", "justifyContent": "flex-end"}),
            ])
        )

    table = dmc.Table(
        highlightOnHover=True,
        striped=True,
        withBorder=False,
        horizontalSpacing="xs",
        verticalSpacing="xs",
        children=[
            html.Thead(html.Tr([html.Th("Ticker"), html.Th("Statut", style={"textAlign": "right"})])),
            html.Tbody(rows),
        ],
    )

    scroll = dmc.ScrollArea(
        type="always",
        offsetScrollbars=True,
        style={"height": 240},
        children=table,
    )

    return scroll 