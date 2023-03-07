import flask
from flask import Flask, jsonify, redirect, request
from datasets import DatasetManager
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics

import requests

app = Flask(__name__)
metrics = PrometheusMetrics(app)
swagger = Swagger(app)

metrics.register_default(
    metrics.counter(
        'response_counter_by_code', 'Counter by response code',
        labels={'code': lambda resp: resp.status_code}
    )
)
metrics.info('api', 'API for Exam', version='1.0.0')

models_host = 'http://host.docker.internal:5001'

dm = DatasetManager()


@app.route('/')
@metrics.counter('root_counter', 'Counter of root requests', labels={
    'status': lambda resp: resp.status_code})
def api_docs():
    return redirect('/apidocs')


@app.route('/types/list')
def get_types_of_models():
    """Returns model types list
    ---
    responses:
      200:
        description: Models type list
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: string
              example: ['GradientBoostingClassifier', 'DecisionTreeClassifier']
    """
    return jsonify(data=['GradientBoostingClassifier', 'DecisionTreeClassifier'])


@app.route('/models/list')
def get_users_models():
    """Returns models list
    ---
    parameters:
      - name: user_id
        in: query
        type: string
        required: false
    responses:
      200:
        description: Models list
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: string
              example: ['model1', 'model2']
    """
    user = get_user(flask.request)
    try:
        response = requests.get(f'{models_host}/get_models', params={
            'user': user
        })
    except Exception:
        return jsonify(message='Model API service not available'), 503
    return response.json(), response.status_code


@app.route('/datasets/list')
def get_datasets():
    """Returns datasets list
    ---
    responses:
      200:
        description: Datasets list
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: string
              example: ['test1', 'test2', 'test3']
    """
    return jsonify(data=dm.get_datasets())


def get_user(req_data):
    """
    Get user from json data or from query parameter
    :param req_data: request
    :return: user_id
    """
    if req_data.json and 'user_id' in req_data.json:
        return str(req_data.json['user_id'])
    else:
        return req_data.args.get('user_id', default='')


def process_json(input_data, model_id, action='train'):
    """
    Preprocess data
    :param input_data: request
    :param model_id: id of model
    :param action: desirable action
    :return: df, personal model_id and model
    """
    values = []
    data = input_data.json
    if action != 'create':
        df_name_from_args = input_data.args.get('df_name', None)
        if (not data or ('data' not in data and 'df_name' not in data)) and not df_name_from_args:
            raise ValueError('There is no data or df_name in request!')
        elif data and 'data' in data:
            values = data['data']
        elif (data and 'df_name' in data) or df_name_from_args:
            df_name = data['df_name'] if (data and 'df_name' in data) else df_name_from_args
            values = dm.get_train(df_name) if action in ['train', 'create_and_train'] else dm.get_test(df_name)

    user_id = get_user(input_data)
    pers_model_id = '_'.join([user_id, model_id])
    if action in ('train', 'test') and pers_model_id not in requests.get(f'{models_host}/get_models').json()['data']:
        raise ModuleNotFoundError('There is no such model!')

    model_type = None
    params = None

    if action in ['create', 'create_and_train']:
        model_type = data['model_type'] if data and 'model_type' in data else 'DecisionTreeClassifier'
        params = data['params'] if data and 'params' in data else {}

    return values, pers_model_id, [model_type, params]


@app.route('/models/delete/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete existing model
    ---
    parameters:
      - name: model_id
        in: path
        type: string
        required: true
      - name: data
        in: body
        type: object
        required: false
        schema:
          type: object
          properties:
            user_id:
              type: string
              example: 123456
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'OK'
    """
    data = flask.request
    user_id = get_user(data)

    pers_model_id = '_'.join([user_id, model_id])
    try:
        response = requests.get(f'{models_host}/delete', params={
            'name': pers_model_id
        })
    except Exception:
        return jsonify(message='Model API didn\'t respond'), 500
    return response.json(), response.status_code


@app.route('/datasets/load/<df_name>', methods=['POST'])
@metrics.summary('load_length', 'Time by response code',
                 labels={'status': lambda resp: resp.status_code})
def load_dataset(df_name):
    """Load new dataset
    ---
    parameters:
      - name: df_name
        in: path
        type: string
        required: true
        description: Name of dataset
      - name: data
        in: body
        type: object
        required: false
        schema:
          type: object
          properties:
            user_id:
              type: string
              example: 123456
            data:
              type: object
              properties:
                X_train:
                  type: array
                  items:
                    type: array
                    items:
                      type: number
                  example: [[0, 0], [0, 1], [1, 0]]
                y_train:
                  type: array
                  items:
                    type: number
                  example: [1, 0, 1]
                X_test:
                  type: array
                  items:
                    type: array
                    items:
                      type: number
                  example: [[1, 1]]
    responses:
      200:
        description: Status of successful operation
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'OK'
      400:
        description: Some input data was bad
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'There is no support of model SomeModel yet!'
    """
    try:
        data = flask.request.json
        if not data or 'data' not in data or len(data['data']) != 3 \
                or 'X_train' not in data['data']\
                or 'y_train' not in data['data']\
                or 'X_test' not in data['data']:
            raise ValueError('data field should contain X_train, y_train and X_test arrays')
        dm.add_dataset(df_name, **data['data'])
    except ValueError as e:
        return jsonify(message=str(e)), 400

    return jsonify(message='OK'), 200


@app.route('/models/create_and_train/<model_id>', methods=['POST'])
@metrics.summary('model_creation_length', 'Time by response code',
                 labels={'status': lambda resp: resp.status_code})
@metrics.gauge('in_progress', 'Requests in progress')
def create_and_train_model(model_id):
    """Creates and trains new model
    ---
    parameters:
      - name: model_id
        in: path
        type: string
        required: true
      - name: data
        in: body
        type: object
        required: false
        schema:
          type: object
          properties:
            model_type:
              type: string
              example: DecisionTreeClassifier
            params:
              type: object
              properties:
                model_parameter:
                  type: string
              example: {max_depth: 3}
            user_id:
              type: string
              example: 123456
            df_name:
              type: string
              example: sample1
    responses:
      200:
        description: Status of successful operation
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'OK'
      400:
        description: Some input data was bad
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'There is no support of model SomeModel yet!'
    """
    data = flask.request
    try:
        values, pers_model_id, model = process_json(data, model_id, action='create_and_train')
        response = requests.post(f'{models_host}/create_and_train', json={
            'model_type': model[0],
            'params': model[1],
            'name': pers_model_id,
            'values': values
        })
    except ValueError as e:
        return jsonify(message=str(e)), 400
    except ModuleNotFoundError as e:
        return jsonify(message=str(e)), 404
    except Exception:
        return jsonify(message='Model API service error'), 500
    return response.json(), response.status_code


@app.route('/models/predict/<model_id>')
@metrics.summary('prediction_length', 'Time by dataframe name',
                 labels={'status': lambda: request.view_args['df_name']})
def get_predict(model_id):
    """Get predicts
    ---
    parameters:
      - name: model_id
        in: path
        type: string
        required: true
      - name: user_id
        in: query
        type: string
        required: false
      - name: df_name
        in: query
        type: string
        required: false
    responses:
      200:
        description: Status of successful operation
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'OK'
            features:
              type: array
              items:
                type: array
                items:
                  type: number
              example: [[0, 0], [0, 1], [1, 0]]
              description: objects to predict
            targets:
              type: array
              items:
                type: number
              example: [1, 0, 1]
              description: Model's predicts
      400:
        description: Predict process failed
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'There is no data or df_name in request!'
      404:
        description: Model not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'There is no such model!'
    """
    data = flask.request
    try:
        values, pers_model_id, _ = process_json(data, model_id, action='test')
        response = requests.put(f'{models_host}/predict', json={
            'name': pers_model_id,
            'values': values
        })
        return response.json(), response.status_code
    except ValueError as e:
        return jsonify(message=str(e)), 400
    except ModuleNotFoundError as e:
        return jsonify(message=str(e)), 404
    except Exception:
        return jsonify(message='Model API service error'), 500


if __name__ == '__main__':
    app.run(port=8080)
