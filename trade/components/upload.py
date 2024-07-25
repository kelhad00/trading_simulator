from dash import html, dcc
def upload_button(id, accept):
    return dcc.Upload(
        id=id,
        accept=accept,
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        className="flex items-center justify-center w-full h-64 bg-gray-100 border-2 border-dashed border-gray-300 rounded-md cursor-pointer",
    )