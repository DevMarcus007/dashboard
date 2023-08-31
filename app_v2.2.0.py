import sqlite3
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from babel.numbers import format_number, format_decimal
from datetime import date
import datetime


conn = sqlite3.connect('operation_base.db')
query = "SELECT * FROM postagens"
df_secap = pd.read_sql_query(query, conn)
conn.close()

df_secap["Data"] = pd.to_datetime(df_secap["Data"], dayfirst=True)
start_date = df_secap["Data"].max()
end_date = df_secap["Data"].max()
timeline_postagem_gccap = df_secap.groupby('Data')['Objeto'].count().tail(15)
timeline_clientes = df_secap[df_secap['Data'] >= timeline_postagem_gccap.index.min()]

def atualiza_base_dados(start_date, end_date):
    primeiro_dia = start_date
    ultimo_dia = end_date
    range_date = df_secap[(df_secap["Data"] >= primeiro_dia) & (df_secap["Data"] <= ultimo_dia)]
    total_postado = range_date.groupby('Cliente')['Objeto'].count()
    total_faturado = range_date.groupby('Cliente')['Valor'].sum()
    clientes_unicos = range_date[range_date['Cliente'] != 'GCCAP']['Cliente'].unique()
    clientes_ordenados = sorted(clientes_unicos, key=lambda c: total_postado.get(c, 0), reverse=True)
    return range_date, total_postado, total_faturado, clientes_unicos, clientes_ordenados


range_date, total_postado, total_faturado, clientes_unicos, clientes_ordenados = atualiza_base_dados(start_date, end_date)


secap_button = dbc.Button(
    [
        dbc.CardImg(
            src="assets/logo_secap.png",
            top=True,
            style={'width': '60px', 'height': '50px', 'margin': '0 auto'},
            className="text-center"
        ),
        dbc.CardBody(
            [
                html.P("Total Captado", className="card-title", style={'font-size': '18px', 'font-weight': 'bolder'}),
                dbc.Row(
                    [
                        dbc.Col(html.P(f"Objetos: {format_number(total_postado.sum(), locale='pt_BR')}"), width="auto", style={'font-size': '15px'}),
                        dbc.Col(html.P(f"Faturamento: R$ {format_decimal(total_faturado.sum(), locale='pt_BR')}"), width="auto", style={'font-size': '15px'}),
                    ],
                    className="my-1 flex-wrap"
                ),
            ]
        ),
    ],
    id="secap-button",
    n_clicks=0,
    className="mb-3 btn btn-outline-secondary btn-lg btn-block btn-3d",
    style={'width': '220px', 'height': '170px', 'background-color': '#F2F2F2'}
)

buttons = [
    dbc.Button(
        [
            dbc.CardImg(
                src=f"assets/logo_{cliente.lower()}.png",
                top=True,
                style={'width': '60px', 'height': '50px', 'margin': '0 auto'},
                className="text-center"
            ),
            dbc.CardBody(
                [
                    html.P(cliente, className="card-title", style={'font-size': '18px', 'font-weight': 'bolder'}),
                    dbc.Row(
                        [
                            dbc.Col(html.P(f"Objetos: {format_number(total_postado.get(cliente, 0), locale='pt_BR')}"), width="auto", style={'font-size': '15px'}),
                            dbc.Col(html.P(f"Faturamento: R$ {format_decimal(total_faturado.get(cliente, 0), locale='pt_BR')}"), width="auto", style={'font-size': '15px'}),
                        ],
                        className="my-1 flex-wrap"
                    ),
                ]
            ),
        ],
        id=f"cliente-button-{cliente}",
        n_clicks=0,
        className="mb-3 btn btn-outline-secondary btn-lg btn-block btn-3d",
        style={'width': '220px', 'height': '170px', 'background-color': '#F2F2F2'}
    )
    for cliente in clientes_ordenados
]

buttons.insert(0, secap_button)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

sidebar = dbc.Nav(buttons, vertical=True, pills=True)

main_content = html.Div(
    [
    
        html.H2(f"Setor de Captação - Operação de {end_date.strftime('%d/%m/%Y')}", className="text-center"),
        html.H2(id='date-selected', className="text-center"),

        html.Div(id='subtitle', className="text-center"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Strong("Serviço", style={'font-size': '16px', 'font-weight': 'bold'})),
                            dbc.CardBody(
                                dcc.Graph(id='graph-servico-bar')
                            ),
                        ],
                        className="mb-3 text-center",
                    ),
                    width={'size': 6, 'sm': 12, 'md': 6}
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Strong("Postagem", style={'font-size': '16px', 'font-weight': 'bold'})),
                            dbc.CardBody(
                                dcc.Graph(id='graph-postagem-bar')
                            ),
                        ],
                        className="mb-3 text-center",
                    ),
                    width={'size': 6, 'sm': 12, 'md': 6}
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Strong("EXPRESSO", style={'font-size': '16px', 'font-weight': 'bold'})),
                            dbc.CardBody(
                                dcc.Graph(id='graph-sedex')
                            ),
                        ],
                        className="mb-3 text-center",
                    ),
                    width={'size': 6, 'sm': 12, 'md': 6}
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Strong("ECONÔMICO", style={'font-size': '16px', 'font-weight': 'bold'})),
                            dbc.CardBody(
                                dcc.Graph(id='graph-pac')
                            ),
                        ],
                        className="mb-3 text-center",
                    ),
                    width={'size': 6, 'sm': 12, 'md': 6}
                ),
            ]
        ),
        dbc.Card(
            [
                dbc.CardHeader(html.Strong("Timeline", style={'font-size': '16px', 'font-weight': 'bold'})),
                dbc.CardBody(
                    dcc.Graph(id='graph-timeline')
                ),
            ],
            className="mb-3 text-center",
        ),

        dbc.Card(
            [
                dbc.CardHeader(html.Strong("Postagem EXPRESSA por Estados", style={'font-size': '16px', 'font-weight': 'bold'})),
                dbc.CardBody(
                    dcc.Graph(id='graph-estados-sdx')
                ),
            ],
            className="mb-3 text-center",
        ),
        dbc.Card(
            [
                dbc.CardHeader(html.Strong("Postagem ECONOMICA por Estados", style={'font-size': '16px', 'font-weight': 'bold'})),
                dbc.CardBody(
                    dcc.Graph(id='graph-estados-pac')
                ),
            ],
            className="mb-3 text-center",
        ),
    ],
    style={"padding": "2rem"},
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width={'size': 2, 'sm': 4, 'md': 3}),
                dbc.Col(main_content, width={'size': 10, 'sm': 8, 'md': 9}),
            ],
            className="py-2",
        ),
    ],
    fluid=True,
    style={"position": "absolute"}
)

def renderizar_botoes_clientes(clientes_ordenados, total_postado, total_faturado):
    botoes_clientes = []
    for cliente in clientes_ordenados:
        botoes_clientes.append(
            dbc.Button(
                [
                    dbc.CardImg(
                        src=f"assets/logo_{cliente.lower()}.png",
                        top=True,
                        style={'width': '80px', 'height': '60px', 'margin': '0 auto'},
                        className="text-center"
                    ),
                    dbc.CardBody(
                        [
                            html.H5(cliente, className="card-title"),
                            dbc.Row(
                                [
                                    dbc.Col(html.P(f"Objetos: {format_number(total_postado.get(cliente, 0), locale='pt_BR')}"), width="auto"),
                                    dbc.Col(html.P(f"Faturamento: R$ {format_decimal(total_faturado.get(cliente, 0), locale='pt_BR')}"), width="auto"),
                                ],
                                className="my-1 flex-wrap"
                            ),
                        ]
                    ),
                ],
                id=f"{cliente}-button",
                n_clicks=0,
                className="mb-3 btn btn-outline-secondary btn-lg btn-block btn-3d",
                style={'width': '300px', 'height': '190px', 'background-color': '#F2F2F2'}
            )
        )
    return botoes_clientes



@app.callback(
    Output('graph-servico-bar', 'figure'),
    Output('graph-postagem-bar', 'figure'),
    Output('graph-sedex', 'figure'),
    Output('graph-pac', 'figure'),
    Output('graph-timeline', 'figure'),
    Output('graph-estados-sdx', 'figure'),
    Output('graph-estados-pac', 'figure'),

    Output('subtitle', 'children'),
    [
        Input('secap-button', 'n_clicks'),
        *[Input(f'cliente-button-{cliente}', 'n_clicks') for cliente in clientes_ordenados]
    ],
   
)

def update_graphs(gccap_clicks, *cliente_clicks):

    ctx = dash.callback_context
    clicked_button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if clicked_button_id == 'secap-button':
        df_filtered = range_date
        total_objetos_por_data = timeline_postagem_gccap
        subtitle = ""
        postagem = range_date.groupby('Postagem')['Objeto'].count()
        servico = range_date.groupby('Serviço')['Objeto'].count().sort_index(ascending=False)
        

    else:
        cliente = clicked_button_id.split('-')[-1]
        df_filtered = range_date[range_date['Cliente'] == cliente]
        timeline_cliente = timeline_clientes[timeline_clientes['Cliente'] == cliente]
        timeline_cliente = timeline_cliente.groupby('Data')['Objeto'].count().tail(15)
        total_objetos_por_data = timeline_cliente
        subtitle = html.H4(f"{cliente}")
        postagem = df_filtered.groupby('Postagem')['Objeto'].count()
        servico = df_filtered.groupby('Serviço')['Objeto'].count().sort_index(ascending=False)
        
           

    total_selex_por_destino = df_filtered[df_filtered['Serviço'] == 'EXPRESSO'].groupby('Destino')['Objeto'].count()
    total_pac_por_destino = df_filtered[df_filtered['Serviço'] == 'ECONÔMICO'].groupby('Destino')['Objeto'].count()
    df_filtered['UF'] = df_filtered['UF'].str.upper()
    estados_sdx = df_filtered[df_filtered['Serviço'] == 'EXPRESSO'].groupby('UF')['Objeto'].count().sort_values(ascending=False)
    estados_pac = df_filtered[df_filtered['Serviço'] == 'ECONÔMICO'].groupby('UF')['Objeto'].count().sort_values(ascending=False)

   
    cores = {'OUTROS ESTADOS': 'red', 'RIO DE JANEIRO': 'green'}
    cores_grafico_sedex = [cores.get(valor, 'gray') for valor in total_selex_por_destino.index]
    cores_grafico_pac = [cores.get(valor, 'gray') for valor in total_pac_por_destino.index]


    fig_sedex = go.Figure(data=[go.Pie(labels=total_selex_por_destino.index, values=total_selex_por_destino.values, marker=dict(colors=cores_grafico_sedex))])
    fig_sedex.update_layout(title="Objetos por Destino")

    fig_pac = go.Figure(data=[go.Pie(labels=total_pac_por_destino.index, values=total_pac_por_destino.values, marker=dict(colors=cores_grafico_pac))])
    fig_pac.update_layout(title="Objetos por Destino")


    cores_servico = {'EXPRESSO': '#FFD700', 'ECONÔMICO': '#0000CD'}
    cores_grafico_servico = [cores_servico.get(valor, 'gray') for valor in servico.index]

    fig_servico = go.Figure(data=[go.Bar(y=servico.index, x=servico.values, orientation='h', marker=dict(color=cores_grafico_servico))])
    fig_servico.update_traces(width=0.35)

    fig_servico.update_layout()

    cores_postagem = {'AUTOMÁTICO': '#FFD700', 'MANUAL': '#0000CD'}
    cores_grafico_postagem = [cores_postagem.get(valor, 'gray') for valor in postagem.index]

    fig_tipo_postagem = go.Figure(data=[go.Bar(y=postagem.index, x=postagem.values, orientation='h', marker=dict(color=cores_grafico_postagem))])
    fig_tipo_postagem.update_traces(width=0.35)

    fig_tipo_postagem.update_layout()  

    fig_timeline = go.Figure(data=[go.Bar(x=total_objetos_por_data.index, y=total_objetos_por_data.values, text=total_objetos_por_data.values, textposition='auto')])
    fig_timeline.update_traces(marker=dict(color='#FFD700'), textangle=0)
    fig_timeline.update_layout(title="Objetos Postados")

    fig_estados_sdx = go.Figure(data=[go.Bar(x=estados_sdx.index, y=estados_sdx.values, text=estados_sdx.values, textposition='auto')])
    fig_estados_sdx.update_traces(marker=dict(color='#FFD700'), textangle=0)
    fig_estados_sdx.update_layout()

    fig_estados_pac = go.Figure(data=[go.Bar(x=estados_pac.index, y=estados_pac.values, text=estados_pac.values, textposition='auto')])
    fig_estados_pac.update_traces(marker=dict(color='#0000CD'), textangle=0)
    fig_estados_pac.update_layout()
   


    return fig_servico, fig_tipo_postagem, fig_sedex, fig_pac, fig_timeline, fig_estados_sdx, fig_estados_pac, subtitle


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)

