#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
from colour import Color
from datetime import datetime
from textwrap import dedent as d
import json

# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Transaction Network"

ACCOUNT="S0001"
TEAM="Logistics"

##############################################################################################################################################################
def network_graph(AccountToSearch, TeamToSearch):

    edge1 = pd.read_csv('CompanyEdgeList.csv')
    node1 = pd.read_csv('CompanyNodeList.csv')

    # filter the record by datetime, to enable interactive control through the input box
    accountSet=set() # contain unique account
    index=0
    if(TeamToSearch=="None" or TeamToSearch==""):
        FirstLetter=""
    else:
        FirstLetter=TeamToSearch[0]
    
    for index in range(0,len(edge1)):
        if(TeamToSearch=="None"):
            if(edge1['Source'][index] != AccountToSearch and edge1['Target'][index] != AccountToSearch):
                edge1.drop(axis=0, index=index, inplace=True)
                continue
            accountSet.add(edge1['Source'][index])
            accountSet.add(edge1['Target'][index])
        else:
            if(edge1['Source'][index] != AccountToSearch and edge1['Target'][index] != AccountToSearch and edge1['Source'][index][0] != FirstLetter and edge1['Target'][index][0] != FirstLetter):
                edge1.drop(axis=0, index=index, inplace=True)
                continue
            accountSet.add(edge1['Source'][index])
            accountSet.add(edge1['Target'][index])

    if(edge1.empty):
        edge1 = pd.read_csv('GraczEdgeList.csv')       
        for index in range(0,len(edge1)):
            accountSet.add(edge1['Source'][index])
            accountSet.add(edge1['Target'][index])

    # to define the centric point of the networkx layout
    shells=[]
    shell1=[]
    shell1.append(AccountToSearch)
    shells.append(shell1)
    shell2=[]
    for ele in accountSet:
        if ele!=AccountToSearch:
            shell2.append(ele)
    shells.append(shell2)

    G = nx.from_pandas_edgelist(edge1, 'Source', 'Target', ['Source', 'Target', 'Type', 'Decision'], create_using=nx.MultiDiGraph())
    nx.set_node_attributes(G, node1.set_index('Code')['Name'].to_dict(), 'Name')
    nx.set_node_attributes(G, node1.set_index('Code')['Team'].to_dict(), 'Team')
    nx.set_node_attributes(G, node1.set_index('Code')['365'].to_dict(), '365')
    nx.set_node_attributes(G, node1.set_index('Code')['Notes'].to_dict(), 'Notes')
    nx.set_node_attributes(G, node1.set_index('Code')['ID'].to_dict(), 'ID')
    # pos = nx.layout.spring_layout(G)
    # pos = nx.layout.circular_layout(G)
    # nx.layout.shell_layout only works for more than 3 nodes
    pos = nx.drawing.layout.planar_layout(G)

    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    if len(shell2)==0:
        traceRecode = []  # contains edge_trace, node_trace, middle_node_trace

        node_trace = go.Scatter(x=tuple([1]), y=tuple([1]), text=tuple([str(AccountToSearch)]), textposition="bottom center",
                                mode='markers+text',
                                marker={'size': 50, 'color': 'LightSkyBlue'})
        traceRecode.append(node_trace)

        node_trace1 = go.Scatter(x=tuple([1]), y=tuple([1]),
                                mode='markers',
                                marker={'size': 50, 'color': 'LightSkyBlue'},
                                opacity=0)
        traceRecode.append(node_trace1)

        figure = {
            "data": traceRecode,
            "layout": go.Layout(title='Interactive Transaction Visualization', showlegend=False,
                                margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                                xaxis={'showgrid': True, 'zeroline': False, 'showticklabels': False},
                                yaxis={'showgrid': True, 'zeroline': False, 'showticklabels': False},
                                height=600
                                )}
        return figure

    traceRecode = []  # contains edge_trace, node_trace, middle_node_trace
    ############################################################################################################################################################

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        if((G.edges[edge]['Type'])=='Goods'):
            linetype='dot'
        else:
            linetype='longdash'
        if(G.edges[edge]['Decision'] == 'F'):
            colortemp='Gray'
        elif(G.edges[edge]['Decision'] == 'Y'):
            colortemp='Lime'
        else:
            colortemp="Red"
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines+text',
                           line={'width': 5, 'dash':linetype},
                           marker=dict(color=colortemp),
                           line_shape='spline',
                           opacity=0.7)
        traceRecode.append(trace)
        index = index + 1
    ###############################################################################################################################################################
    #node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
     #                       hoverinfo="text", marker={'size': 50, 'color': 'LightSkyBlue'})

    index = 0
    for node in G.nodes():
        xset, yset = G.nodes[node]['pos']
        hovertextset = "Name: " + str(G.nodes[node]['Name']) + "<br>" + "Team: " + str(G.nodes[node]['Team'])
        textset = str(G.nodes[node]['ID'])
        #textset = TeamToSearch
        textcolor='Black'
        if(str(G.nodes[node]['Team'])=='Logistics'):
            colortemp='LightSkyBlue'
        elif(str(G.nodes[node]['Team'])=='Sales'):
            colortemp='Goldenrod'
        elif(str(G.nodes[node]['Team'])=='Production'):
            colortemp='Pink'
        elif(str(G.nodes[node]['Team'])=='Marketing'):
            colortemp='LightGreen'
        elif(str(G.nodes[node]['Team'])=='Accounting'):
            colortemp='LightGray'
        else:
            colortemp='Black'
            textcolor='White'
        node_trace = go.Scatter(x=tuple([xset]),
                                y=tuple([yset]),
                                hovertext=tuple([hovertextset]),
                                text=tuple([textset]),
                                mode='markers+text',
                                textfont={'family':'sans serif', 'size':10, 'color':textcolor},
                                textposition="middle center",
                                hoverinfo="text",
                                marker={'size': 40, 'color': colortemp},
                                opacity=1)
        index = index + 1
        traceRecode.append(node_trace)
    ################################################################################################################################################################
    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', hoverinfo="text",
                                    marker={'size': 20, 'color': 'LightSkyBlue'},
                                    opacity=0)

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        if(G.edges[edge]['Decision'] != 'F'):
            textset=G.edges[edge]['Decision']
        else:
            textset="None"     
        hovertext = "From: " + str(G.edges[edge]['Source']) + "<br>" + "To: " + str(G.edges[edge]['Target']) + "<br>" + "Type: " + str(G.edges[edge]['Type']) + "<br>" + "Decision: " + str(textset)
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    traceRecode.append(middle_hover_trace)
    #################################################################################################################################################################
    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Interactive Flowchart Visualization', showlegend=False, hovermode='closest',
                            margin={'b': 0, 'l': 0, 'r': 0, 't': 0},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=800,
                            width=1300,
                            clickmode='event+select',
                            annotations=[
                                dict(
                                    ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                                    ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                                    x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                                    y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                                    showarrow=True,
                                    arrowhead=2,
                                    arrowsize=3,
                                    arrowwidth=1.5,
                                    opacity=1
                                ) for edge in G.edges]
                            )}
    return figure
######################################################################################################################################################################
# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    #########################Title
    html.Div([html.H1("Work Flowchart")],
             className="row",
             style={'textAlign': "center"}),
    #############################################################################################define the row
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            **Datapoint To Search**

                            Input the data point to visualize.
                            """)),
                            dcc.Input(id="input1", type="text", placeholder="Account"),
                            html.Div(id="output")
                        ],
                        style={'height': '300px'}),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            **Team To Search**

                            Input the Team to visualize.
                            """)),
                            dcc.RadioItems(
                                id="input2",
                                options=[
                                    {'label': 'All', 'value': 'None'},
                                    {'label': 'Accounting', 'value': 'Accounting'},
                                    {'label': 'Logistics', 'value': 'Logistics'},
                                    {'label': 'Marketing', 'value': 'Marketing'},
                                    {'label': 'Production', 'value': 'Production'},
                                    {'label': 'Sales', 'value': 'Sales'}
                                    ],
                                value=''
                                ),
                            html.Div(id="output2")
                        ],
                        style={'height': '300px'}),
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=network_graph(ACCOUNT,TEAM))],
            ),

            #########################################right side two output component
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Hover Data**

                            Mouse over values in the graph.
                            """)),
                            html.Pre(id='hover-data', style=styles['pre'])
                        ],
                        style={'height': '400px'}),

                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Click Data**

                            Click on points in the graph.
                            """)),
                            html.Pre(id='click-data', style=styles['pre'])
                        ],
                        style={'height': '400px'})
                ]
            )
        ]
    )
])

###################################callback for left side components
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('input1', 'value'), dash.dependencies.Input('input2', 'value')])
def update_output(input1, input2):
    ACCOUNT = input1
    TEAM = str(input2)
    return network_graph(input1, str(input2))

################################callback for right side components
@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('my-graph', 'hoverData')])
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('my-graph', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)



if __name__ == '__main__':
    app.run_server(debug=True)
