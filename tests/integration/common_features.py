import json

from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc

PASS = 'passed'
FAIL = 'failed'


def simple_app_layout(
        component
):
    return [
        dcc.Input(id='prop-name'),
        dcc.Input(id='prop-value'),
        html.Div(id='pass-fail-div'),
        html.Button('Submit', id='submit-prop-button'),
        component
    ]


def simple_app_callback(
        app,
        dash_duo,
        component_id,
        test_prop_name,
        test_prop_value,
        process_value=None,
        validation_fn=None,
        take_snapshot=False
):
    if validation_fn is None:
        def validation_fn(x): return x == test_prop_value

    if process_value is None:
        def process_value(x): return x

    @app.callback(
        Output(component_id, test_prop_name),
        [Input('submit-prop-button', 'n_clicks')],
        [State('prop-value', 'value')]
    )
    def setup_click_callback(nclicks, value):
        if nclicks is not None and nclicks > 0:
            return process_value(value)
        return None

    @app.callback(
        Output('pass-fail-div', 'children'),
        [Input(component_id, test_prop_name)],
        [State('submit-prop-button', 'n_clicks')]
    )
    def simple_callback(prop_value, nclicks):
        if nclicks is None or nclicks == 0:
            return None
        passfail = PASS if validation_fn(prop_value) else FAIL
        return html.Div(passfail, id='passfail')

    dash_duo.start_server(app)
    dash_duo.wait_for_element('#'+component_id)

    input_prop_name = dash_duo.find_element('#prop-name')
    input_prop_value = dash_duo.find_element('#prop-value')

    input_send_button = dash_duo.find_element('#submit-prop-button')

    input_prop_name.send_keys(test_prop_name)
    input_prop_value.send_keys(test_prop_value)
    input_send_button.click()

    dash_duo.wait_for_element('#passfail')

    if take_snapshot:
        dash_duo.percy_snapshot(f'{component_id}_{test_prop_name}_{test_prop_value}')

    assert dash_duo.find_element('#passfail').text == PASS


def nested_component_layout(
        component
):
    return [
        dcc.Input(id='prop-name'),
        dcc.Input(id='prop-value'),
        html.Div(id='pass-fail-div'),
        html.Button('Submit', id='submit-prop-button'),
        dcc.Graph(
            id='test-graph',
            figure=component
        )
    ]


def nested_component_app_callback(
        app,
        dash_duo,
        component,
        component_data,
        test_prop_name,
        test_prop_value,
        data_prop_name='data',
        extra_props=None,
        process_value=None,
        path_to_test_prop=None,
        take_snapshot=False
):

    if process_value is None:
        def process_value(x): return x

    component_props = {}

    if extra_props is not None:
        component_props = extra_props

    component_props[data_prop_name] = component_data

    @app.callback(
        Output('test-graph', 'figure'),
        [Input('submit-prop-button', 'n_clicks')],
        [State('prop-value', 'value')]
    )
    def setup_click_callback(nclicks, prop_value):
        if nclicks is not None and nclicks > 0:
            component_props[test_prop_name] = process_value(prop_value)
        return component(**component_props)

    @app.callback(
        Output('pass-fail-div', 'children'),
        [Input('test-graph', 'figure')],
        [State('submit-prop-button', 'n_clicks')]
    )
    def nested_callback(fig, nclicks):
        if nclicks is None or nclicks == 0:
            return None
        if path_to_test_prop:
            # if this is a nested property of the figure,
            # ensure that it has been passed correctly
            passfail = PASS if json.dumps(eval('fig' + path_to_test_prop)) == \
                test_prop_value else FAIL
        else:
            # no other way to check if a prop that goes
            # to the clustergram has been passed correctly
            passfail = PASS
        return html.Div(passfail, id='passfail')

    dash_duo.start_server(app)
    dash_duo.wait_for_element('#test-graph')

    input_prop_name = dash_duo.find_element('#prop-name')
    input_prop_value = dash_duo.find_element('#prop-value')

    input_send_button = dash_duo.find_element('#submit-prop-button')

    input_prop_name.send_keys(test_prop_name)
    input_prop_value.send_keys(test_prop_value)
    input_send_button.click()

    dash_duo.wait_for_element('#passfail')

    if take_snapshot:
        dash_duo.percy_snapshot(f'{component.__name__}_{test_prop_name}{test_prop_value}')

    assert dash_duo.find_element('#passfail').text == PASS