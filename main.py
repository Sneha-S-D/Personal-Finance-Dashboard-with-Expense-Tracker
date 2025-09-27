import sqlite3
from flask import Flask, g
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd

DATABASE = "expenses.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_db(e=None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

server = Flask(__name__)
server.config.from_mapping(DATABASE=DATABASE)
server.teardown_appcontext(close_db)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.title = 'Expense Tracker'

app.layout = html.Div([
    html.H1("Expense Tracker", style={'textAlign': 'center', 'marginBottom': '20px'}),

    dcc.Tabs([
        dcc.Tab(label='New Expense', children=[
            html.Div([
                html.Label('Date of the Expense (dd-mm-yyyy):'),
                dcc.Input(id='Date', type='text', placeholder="dd-mm-yyyy", style={'width': '100%'}), html.Br(),
                html.Label('Description of the Expense:'),
                dcc.Input(id='description', type='text', placeholder="What did you buy?", style={'width': '100%'}), html.Br(),
                html.Label('Category:'),
                dcc.Input(id='CATEGORY', type='text', placeholder='Category', style={'width': '100%'}), html.Br(),
                html.Label('Price of the Expense:'),
                dcc.Input(id='price', type="number", placeholder="0.00", style={'width': '100%'}), html.Br(),
                html.Button('Track', id='submit-button', n_clicks=0, style={'marginTop': '10px', 'width': '100%'})
            ], style={'maxWidth': '500px', 'margin': 'auto'})
        ]),

        dcc.Tab(label='View Expenses', children=[
            html.Div([
                html.Div(id='expense-table', style={'overflowX': 'auto', 'marginTop': '20px'}),
                html.Div(id='some-output-element', style={'marginTop': '20px'})
            ], style={'maxWidth': '900px', 'margin': 'auto'})
        ]),

        dcc.Tab(label='Category Based Pie Chart', children=[
            html.Div([
                dcc.Graph(id='pie_chart_category', figure={'data': [], 'layout': {}}, style={'height': '500px'})
            ], style={'maxWidth': '700px', 'margin': 'auto'})
        ])
    ])
])

@app.callback(
    Output('pie_chart_category', 'figure'),
    [Input('submit-button', 'n_clicks')]
)
def update_pie_chart_category(n_clicks):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT CATEGORY, COUNT(*) FROM expenses GROUP BY CATEGORY")
    category_data = cur.fetchall()

    labels = [row[0] for row in category_data]
    values = [row[1] for row in category_data]

    return {
        'data': [{'labels': labels, 'values': values, 'type': 'pie', 'hoverinfo': 'label+percent', 'textinfo': 'value+percent'}],
        'layout': {'title': 'Transactions by Category'}
    }

@app.callback(
    Output('expense-table', 'children'),
    [Input('submit-button', 'n_clicks')]
)
def update_expense_table(n_clicks):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY Date DESC")
    expenses = cur.fetchall()
    df = pd.DataFrame(expenses, columns=['ID', 'Date', 'Description', 'Category', 'Price'])
    if df.empty:
        return 'No expenses to display.'

    table = html.Table(
        [html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([html.Td(exp[col]) for col in df.columns]) for _, exp in df.iterrows()],
        style={'width': '100%', 'borderCollapse': 'collapse'}
    )
    return table

@app.callback(
    [Output('some-output-element', 'children'),
     Output('Date', 'value'),
     Output('description', 'value'),
     Output('CATEGORY', 'value'),
     Output('price', 'value')],
    [Input('submit-button', 'n_clicks')],
    [State('Date', 'value'),
     State('description', 'value'),
     State('CATEGORY', 'value'),
     State('price', 'value')]
)
def handle_form_submission(n_clicks, date, description, category, price):
    if n_clicks > 0:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (Date, description, CATEGORY, price) VALUES (?, ?, ?, ?)",
                    (date, description, category, price))
        conn.commit()

        message = f"Recent Expense:<br>Date: {date}<br>Description: {description}<br>Category: {category}<br>Price: {price}"
        return (dcc.Markdown(message, dangerously_allow_html=True), '', '', '', 0)
    return ("", date, description, category, price)

if __name__ == '__main__':
    app.run_server(debug=True)
