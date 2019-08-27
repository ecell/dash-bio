import os
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bio
import dash_cytoscape as cyto
import pandas as pd

# running directly with Python
if __name__ == '__main__':
    from utils.app_standalone import run_standalone_app

PATHWAY_WIDTH = 800
PATHWAY_HEIGHT = 600

def header_colors():
    return {
        'bg_color': '#232323',
        'font_color': 'white'
    }

def description():
    return 'Display KEGG pathway with user data. \
    Perfect for visualization of gene expression data.'

def layout():
    return html.Div(id='keggscape-body', className='app-body', children=[
        dcc.Loading(className='dashbio-loading', children=html.Div(
            id='ks-graph-div',
            children=dash_bio.KeggScape(pathwayid="eco00020", width=PATHWAY_WIDTH, height=PATHWAY_HEIGHT),
            style={'display': 'flex'}
        )),
        html.Div(id='keggscape-control-tabs', className='control-tabs', children=[
            dcc.Tabs(id='ks-tabs', value='what-is', children=[

                dcc.Tab(
                    label='About',
                    value='what-is',
                    children=html.Div(className='control-tab', children=[
                        html.H4(className='what-is', children='What is KEGGscape?'),
                        html.P('KEGGscape imports KEGG pathway and visualize it with Cytoscape.js.'),
                        html.P('KEGGscape also integrate your Omics-data with the KEGG pathway.'),
                        html.P('KEGGscape can be combined with the other Dash components.')
                    ])
                ),

                dcc.Tab(
                    label='Data',
                    value='data',
                    children=html.Div(className='control-tab', children=[

                        html.Div(
                            'KEGG pathway ID',
                            title='Choose KEGG pathway you want to import',
                            className='fullwidth-app-controls-name',
                        ),

                        dcc.Input(id='ks-pathwayid', type='text', value='eco00020'),

                        html.Br(),

                        html.Div(
                            'Upload dataset',
                            title='Upload your own dataset below',
                            className='app-controls-name'
                        ),

                        dcc.Input(id='ks-datafilepath', type='text', value='Fill the file path to your data'),

                    ])
                ),

                dcc.Tab(
                    label='Style',
                    value='style', children=html.Div(className='control-tab', children=[
                        html.Div(className='app-controls-block', children=[
                            html.Div(
                                className='app-control-name',
                                children='Visual styling UI is not implemented yet.'
                            )
                        ])
                    ])
                )

            ])
        ])
    ])

def callbacks(app):
    @app.callback(
        Output('ks-graph-div', 'children'),
        [
            Input('ks-pathwayid', 'value'),
            Input('ks-datafilepath', 'value'),
        ]
    )
    def update_graph(pathway_id, datafilepath):
        """Update rendering of KEGG pathway."""
        # print(pathway_id)
        df = pd.read_csv(datafilepath)
        #print(df.head())
        return dash_bio.KeggScape(
            pathwayid = pathway_id,
            width = PATHWAY_WIDTH,
            height = PATHWAY_HEIGHT,
            df=df
        )

    @app.callback(
        Output('cytoscape-node-table', 'style_data_conditional'),
        [
            Input('cytoscape', 'tapNodeData'),
            Input('cytoscape-node-table', 'data')                                                                                                                                                                      ]
    )
    def update_node_table(tapdata, tabledata):
        # print(tapdata)
        tapped_id = tapdata['id']
        row_index = 0
        for row in tabledata:
            if row['id'] == tapped_id:
                return [{
                    "if": {"row_index": row_index},
                    "backgroundColor": "#3D9970",
                    'color': 'white'
                }]
            row_index = row_index+1

# only declare app/server if the file is being run directly
if 'DASH_PATH_ROUTING' in os.environ or __name__ == '__main__':
    app = run_standalone_app(layout, callbacks, header_colors, __file__)
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, port=18050)
    
