import sqlite3
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from babel.numbers import format_number, format_decimal, format_currency
from datetime import date, datetime
import json
import requests
import plotly.express as px

conn = sqlite3.connect('operation_base.db')
query = "SELECT * FROM postagens"
df_secap = pd.read_sql_query(query, conn)
conn.close()

df_secap["Data"] = pd.to_datetime(df_secap["Data"], dayfirst=True)
start_date = df_secap["Data"].max()
end_date = df_secap["Data"].max()
timeline_postagem_secap = df_secap.groupby('Data')['Objeto'].count().tail(15)
timeline_clientes = df_secap[df_secap['Data'] >= timeline_postagem_secap.index.min()]

geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
response = requests.get(geojson_url)
geojson_data = response.json()

def atualiza_base_dados(start_date, end_date):
    range_date = df_secap[(df_secap["Data"] >= start_date) & (df_secap["Data"] <= end_date)]
    total_postado = range_date.groupby('Cliente')['Objeto'].count()
    total_faturado = range_date.groupby('Cliente')['Valor'].sum()
    clientes_unicos = sorted(range_date['Cliente'].unique())
    return range_date, total_postado, total_faturado, clientes_unicos


range_date, total_postado, total_faturado, clientes_unicos = atualiza_base_dados(start_date, end_date)


secap_button = dbc.Button(
    [
        dbc.CardImg(
            src="assets/logo_secap.png",
            top=True,
            style={'width': '90px', 'height': '75px', 'margin': '0 auto'},
            className="text-center"
        ),
        dbc.CardBody(
            [
                html.P("Setor de Captação", className="card-title", style={'font-size': '18px', 'font-weight': 'bolder'}),
            ]
        ),
    ],
    id="secap-button",
    n_clicks=0,
    className="mb-3 btn btn-outline-secondary btn-lg btn-block btn-3d",
    style={'width': '200px', 'height': '150px', 'background-color': '#F2F2F2'}
)

buttons = [
    dbc.Button(
        [
            dbc.CardImg(
                src=f"assets/logo_{cliente.lower()}.png",
                top=True,
                style={'width': '90px', 'height': '75px', 'margin': '0 auto'},
                className="text-center"
            ),
            dbc.CardBody(
                [
                    html.P(cliente, className="card-title", style={'font-size': '18px', 'font-weight': 'bolder'}),
                ]
            ),
        ],
        id=f"cliente-button-{cliente}",
        n_clicks=0,
        className="mb-3 btn btn-outline-secondary btn-lg btn-block btn-3d",
        style={'width': '200px', 'height': '150px', 'background-color': '#F2F2F2'}
    )
    for cliente in clientes_unicos
]

buttons.insert(0, secap_button)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

sidebar = dbc.Nav(buttons, vertical=True, pills=True)

main_content = html.Div(
    [html.Div(
        [
            dcc.DatePickerSingle(
                id='start-date-picker-single',
                date = end_date,
                calendar_orientation = 'vertical',
                clearable = True,
                with_portal=True,
                display_format='DD/MM/YYYY',
                className='mb-4'
            ),
            dcc.DatePickerSingle(
                id='end-date-picker-single',
                date = end_date,
                calendar_orientation = 'vertical',
                clearable = True,
                with_portal=True,
                display_format='DD/MM/YYYY',
                className='mb-4'
            ),
            html.Button('Alterar Data', id='alterar-button', className='btn btn-primary ml-2', style={"height":'46px'}),

        ],
        className='d-flex justify-content-end'
    ),
    
        html.H2(id='date-selected', className="text-center"),

        html.Div(id='subtitle', className="text-center"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Strong("Postagem", style={'font-size': '16px', 'font-weight': 'bold'})),
                            dbc.CardBody(
                                dcc.Graph(id='graph-postagem-funil')
                            ),
                        ],
                        className="mb-3 text-center",
                    ),
                    width={'size': 6, 'sm': 12, 'md': 6}
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Strong("Faturamento", style={'font-size': '16px', 'font-weight': 'bold'})),
                            dbc.CardBody(
                                dcc.Graph(id='graph-faturamento-funil')
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
                            dbc.CardHeader(html.Strong("Tipo", style={'font-size': '16px', 'font-weight': 'bold'})),
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
                                dcc.Graph(id='graph-expresso')
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
                                dcc.Graph(id='graph-economico')
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
                                dcc.Graph(id='graph-estados-expresso')
                            ),
                        ],
                        className="mb-3 text-center",
                    ),
                    
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Strong("Postagem ECONOMICA por Estados", style={'font-size': '16px', 'font-weight': 'bold'})),
                            dbc.CardBody(
                                dcc.Graph(id='graph-estados-economico')
                            ),
                        ],
                        className="mb-3 text-center",
                    ),
                   

        dcc.Location(id='url', refresh=True),

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

@app.callback(
    Output('start-date-picker-single', 'date'),
    Output('end-date-picker-single', 'date'),
    Output('date-selected', 'children'),
    Output('url', 'pathname'),
    [Input('alterar-button', 'n_clicks')],
    [State('start-date-picker-single', 'date'),
    State('end-date-picker-single', 'date'),
    ]
)
def update_dates(n_clicks, date1, date2):
    global start_date, end_date
    if n_clicks is not None:
        if date1 and date2:
            start_date = date1
            end_date = date2
    new_start_date = date1

    if start_date == end_date:
        if start_date != new_start_date:
            date_selected =  html.H2(f"Operação De {start_date.strftime('%d/%m/%Y')}", className="text-center")
        else:
            date_selected =  html.H2(f"Operação De {new_start_date[8:10]}/{new_start_date[5:7]}/{new_start_date[:4]}", className="text-center")
    else:
        date_selected =  html.H2(f"Operação De {start_date[8:10]}/{start_date[5:7]}/{start_date[:4]} a {end_date[8:10]}/{end_date[5:7]}/{end_date[:4]}", className="text-center")


    return start_date, end_date, date_selected, '/'

@app.callback(
    [   Output('graph-postagem-funil', 'figure'),
        Output('graph-faturamento-funil', 'figure'),
        Output('graph-servico-bar', 'figure'),
        Output('graph-postagem-bar', 'figure'),
        Output('graph-expresso', 'figure'),
        Output('graph-economico', 'figure'),
        Output('graph-timeline', 'figure'),
        Output('graph-estados-expresso', 'figure'),
        Output('graph-estados-economico', 'figure'),
        Output('subtitle', 'children'),
    ],
    [
        Input('secap-button', 'n_clicks'),
        *[Input(f'cliente-button-{cliente}', 'n_clicks') for cliente in clientes_unicos]
    ],
    
)
def update_graphs(gccap_clicks, *cliente_clicks ):
   
    range_date, total_postado, total_faturado, clientes_unicos = atualiza_base_dados(start_date, end_date)

    ctx = dash.callback_context
    clicked_button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if clicked_button_id == 'secap-button':
        df_filtered = range_date
        total_objetos_por_data = timeline_postagem_secap
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
        
           

    total_expresso_por_destino = df_filtered.loc[df_filtered['Serviço'] == 'EXPRESSO'].groupby('Destino')['Objeto'].count()
    total_economico_por_destino = df_filtered.loc[df_filtered['Serviço'] == 'ECONÔMICO'].groupby('Destino')['Objeto'].count()
    df_filtered.loc[:, 'UF'] = df_filtered['UF'].str.upper()

   
    cores = {'OUTROS ESTADOS': 'red', 'RIO DE JANEIRO': 'green'}
    cores_grafico_expresso = [cores.get(valor, 'gray') for valor in total_expresso_por_destino.index]
    cores_grafico_economico = [cores.get(valor, 'gray') for valor in total_economico_por_destino.index]

    postagens_por_cliente = range_date.groupby('Cliente')['Objeto'].count().reset_index()
    postagens_por_cliente.rename(columns={'Objeto': 'Postagens'}, inplace=True)

    expresso_por_cliente = range_date[range_date['Serviço'] == 'EXPRESSO'].groupby('Cliente')['Objeto'].count().reset_index()
    expresso_por_cliente.rename(columns={'Objeto': 'Expresso'}, inplace=True)

    economico_por_cliente = range_date[range_date['Serviço'] == 'ECONÔMICO'].groupby('Cliente')['Objeto'].count().reset_index()
    economico_por_cliente.rename(columns={'Objeto': 'Econômico'}, inplace=True)

    resultado_postagem = postagens_por_cliente.merge(expresso_por_cliente, on='Cliente', how='left').merge(economico_por_cliente, on='Cliente', how='left')

    resultado_postagem.fillna(0, inplace=True)
    resultado_postagem.sort_values(by='Postagens', ascending=False, inplace=True)
    resultado_postagem = resultado_postagem.reset_index(drop=True)
    

    melted_df = pd.melt(resultado_postagem, id_vars=['Cliente'], value_vars=['Expresso', 'Econômico'], var_name='Tipo', value_name='Quantidade')

    melted_df['Cor'] = melted_df['Tipo'].map({'Expresso': '#FFD700', 'Econômico': '#0000CD'})


    resultado_postagem['Porcentagem_Expresso'] = (resultado_postagem['Expresso'] / resultado_postagem['Postagens']) * 100
    resultado_postagem['Porcentagem_Econômico'] = (resultado_postagem['Econômico'] / resultado_postagem['Postagens']) * 100

    resultado_postagem = resultado_postagem.sort_values(by='Postagens', ascending=False)

    fig_postagem = go.Figure()

    fig_postagem.add_trace(go.Bar(
        y=resultado_postagem['Cliente'],
        x=resultado_postagem['Expresso'],
        name='Expresso',
        orientation='h',
        marker=dict(color='#FFD700'),
        hovertemplate='Expresso: %{x} Objetos<br>%{customdata[0]:.2f}%'
    ))

    fig_postagem.add_trace(go.Bar(
        y=resultado_postagem['Cliente'],
        x=resultado_postagem['Econômico'],
        name='Econômico',
        orientation='h',
        marker=dict(color='#0000CD'),
        hovertemplate="Econômico: %{x} Objetos<br>%{customdata[1]:.2f}%",
    ))

    for i, total in enumerate(resultado_postagem['Postagens']):
        fig_postagem.add_annotation(
            x=total,
            y=resultado_postagem['Cliente'][i],
            text=total,
            showarrow=False,
            xref='x',  
            yref='y',  
            xshift=25, 
            font=dict(size=12, color='black')
        )

    fig_postagem.update_layout(

        barmode='stack',
        legend=dict(title_text='  Serviço', x=0.35, y=1.3),
    )

    fig_postagem.update_traces(
        customdata=resultado_postagem[['Porcentagem_Expresso', 'Porcentagem_Econômico']],
    )

    faturamento_por_cliente = range_date.groupby('Cliente')['Valor'].sum().reset_index()
    valor_expresso_por_cliente = range_date[range_date['Serviço'] == 'EXPRESSO'].copy()
    valor_expresso_por_cliente = valor_expresso_por_cliente.groupby('Cliente')['Valor'].sum().reset_index()
    valor_expresso_por_cliente.rename(columns={'Valor': 'Expresso'}, inplace=True)

    valor_economico_por_cliente = range_date[range_date['Serviço'] == 'ECONÔMICO'].copy()
    valor_economico_por_cliente = valor_economico_por_cliente.groupby('Cliente')['Valor'].sum().reset_index()
    valor_economico_por_cliente.rename(columns={'Valor': 'Econômico'}, inplace=True)

    resultado_faturamento = faturamento_por_cliente.merge(valor_expresso_por_cliente, on='Cliente', how='left')
    resultado_faturamento = resultado_faturamento.merge(valor_economico_por_cliente, on='Cliente', how='left')

    resultado_faturamento.fillna(0, inplace=True)
    resultado_faturamento.rename(columns={'Valor': 'Faturamento'}, inplace=True)
    resultado_faturamento.sort_values(by='Faturamento', ascending=False, inplace=True)
    resultado_faturamento = resultado_faturamento.reset_index(drop=True)

    resultado_faturamento['Porcentagem_Expresso'] = (resultado_faturamento['Expresso'] / resultado_faturamento['Faturamento']) * 100
    resultado_faturamento['Porcentagem_Econômico'] = (resultado_faturamento['Econômico'] / resultado_faturamento['Faturamento']) * 100

    resultado_faturamento = resultado_faturamento.sort_values(by='Faturamento', ascending=False)

    fig_faturamento = go.Figure()

    fig_faturamento.add_trace(go.Bar(
        y=resultado_faturamento['Cliente'],
        x=resultado_faturamento['Expresso'],
        name='Expresso',
        orientation='h',
        marker=dict(color='#FFD700'),
        hovertemplate='Expresso: R$ %{x:$.,2f}<br>%{customdata[0]:.2f}%'
    ))

    fig_faturamento.add_trace(go.Bar(
        y=resultado_faturamento['Cliente'],
        x=resultado_faturamento['Econômico'],
        name='Econômico',
        orientation='h',
        marker=dict(color='#0000CD'),
        hovertemplate="Econômico: R$ %{x:$.,2f}<br>%{customdata[1]:.2f}%",
    ))

    for i, total in enumerate(resultado_faturamento['Faturamento']):
        formatted_value = format_currency(total, 'BRL', locale='pt_BR')
        fig_faturamento.add_annotation(
            x=total,
            y=resultado_faturamento['Cliente'][i],
            text=formatted_value,
            showarrow=False,
            xref='x',  
            yref='y',  
            xshift=45, 
            font=dict(size=12, color='black')
        )

    fig_faturamento.update_layout(
        barmode='stack',
        legend=dict(title_text='  Serviço', x=0.35, y=1.3),
    )

    fig_faturamento.update_traces(
        customdata=resultado_faturamento[['Porcentagem_Expresso', 'Porcentagem_Econômico']],
    )

    fig_expresso = go.Figure(data=[go.Pie(labels=total_expresso_por_destino.index, values=total_expresso_por_destino.values, marker=dict(colors=cores_grafico_expresso))])
    fig_expresso.update_layout(title="Objetos por Destino")
    fig_expresso.update_layout(autosize=True)

    fig_economico = go.Figure(data=[go.Pie(labels=total_economico_por_destino.index, values=total_economico_por_destino.values, marker=dict(colors=cores_grafico_economico))])
    fig_economico.update_layout(title="Objetos por Destino")
    fig_economico.update_layout(autosize=True)


    cores_servico = {'EXPRESSO': '#FFD700', 'ECONÔMICO': '#0000CD'}
    cores_grafico_servico = [cores_servico.get(valor, 'gray') for valor in servico.index]

    fig_servico = go.Figure(data=[go.Bar(y=servico.index, x=servico.values, orientation='h', marker=dict(color=cores_grafico_servico))])
    fig_servico.update_traces(width=0.35)

    fig_servico.update_layout(autosize=True)

    cores_postagem = {'AUTOMÁTICO': '#FFD700', 'MANUAL': '#0000CD'}
    cores_grafico_postagem = [cores_postagem.get(valor, 'gray') for valor in postagem.index]

    fig_tipo_postagem = go.Figure(data=[go.Bar(y=postagem.index, x=postagem.values, orientation='h', marker=dict(color=cores_grafico_postagem))])
    fig_tipo_postagem.update_traces(width=0.35)

    fig_tipo_postagem.update_layout(autosize=True)

    fig_timeline = go.Figure(data=[go.Bar(x=total_objetos_por_data.index, y=total_objetos_por_data.values, text=total_objetos_por_data.values, textposition='auto')])
    fig_timeline.update_traces(marker=dict(color='#FFD700'), textangle=0)
    fig_timeline.update_layout(title="Objetos Postados")
    fig_timeline.update_layout(autosize=True)

    todos_estados = pd.DataFrame({'UF': range_date.UF.unique()})
    total_expresso_por_destino = df_filtered[df_filtered['Serviço'] == 'EXPRESSO']
    total_economico_por_destino = df_filtered[df_filtered['Serviço'] == 'ECONÔMICO']
   
    total_postagem_por_estado = total_expresso_por_destino.groupby('UF')['Objeto'].count().reset_index()

    dados_postagem_estados = todos_estados.merge(total_postagem_por_estado, on='UF', how='left').fillna(0)

    fig_estados_expresso = px.choropleth(dados_postagem_estados,
                        geojson=geojson_data,
                        locations='UF',
                        featureidkey="properties.sigla",
                        color='Objeto',
                        hover_name='UF',
                        color_continuous_scale='matter',
                        labels={'Objeto': 'Quantidade de Objetos'},
                        template='plotly')

    fig_estados_expresso.update_geos(fitbounds="locations", visible=False)
    


    total_postagem_por_estado = total_economico_por_destino.groupby('UF')['Objeto'].count().reset_index()

    dados_postagem_estados = todos_estados.merge(total_postagem_por_estado, on='UF', how='left').fillna(0)

    fig_estados_economico = px.choropleth(dados_postagem_estados,
                        geojson=geojson_data,
                        locations='UF',
                        featureidkey="properties.sigla",
                        color='Objeto',
                        hover_name='UF',
                        color_continuous_scale='matter',
                        labels={'Objeto': 'Quantidade de Objetos'},
                        template='plotly')

    fig_estados_economico.update_geos(fitbounds="locations", visible=False)
    



    return fig_postagem, fig_faturamento, fig_servico, fig_tipo_postagem, fig_expresso, fig_economico, fig_timeline, fig_estados_expresso, fig_estados_economico, subtitle

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)

