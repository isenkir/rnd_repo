from user_models import ModelsManager
from models.factory import ModelsFactory
import flask
from flask import Flask, jsonify
import numpy as np

mm = ModelsManager()
mf = ModelsFactory()
app = Flask(__name__)


@app.route('/delete')
def delete_model():
    name = flask.request.args.get('name')
    mm.delete_model(name)

    return jsonify(message='OK'), 200


@app.route('/create', methods=['POST'])
def create_model():
    model_name, model_type, params = \
        flask.request.json['model_name'], \
        flask.request.json['model_type'], \
        flask.request.json['params']

    try:
        model = mf.get_model(model_type, params)
        mm.add_model(model_name, model, model_type, params)
    except ValueError as e:
        return jsonify(message=str(e)), 400

    return jsonify(message='OK'), 200


@app.route('/predict', methods=['PUT'])
def get_predict_for_model():
    try:
        name, values = flask.request.json['name'], flask.request.json['values']
        predicts = list(map(int, mm.get_model(name).predict(np.array(values))))
    except ValueError as e:
        return jsonify(message=str(e)), 400
    except ModuleNotFoundError as e:
        return jsonify(message=str(e)), 404
    except Exception as e:
        return jsonify(message=str(e)), 400

    return jsonify(message='OK',
                   features=values,
                   targets=predicts), 200


@app.route('/train', methods=['PUT'])
def train_model():
    try:
        name, values = flask.request.json['name'], flask.request.json['values']
        fitted_model = mm.get_model(name).fit(*values)
        mm.add_model(name, fitted_model)
    except ValueError as e:
        return jsonify(message=str(e)), 400
    except ModuleNotFoundError as e:
        return jsonify(message=str(e)), 404

    return jsonify(message='OK'), 200


@app.route('/create_and_train', methods=['POST'])
def create_and_train_model():
    try:
        model_type, params, name, values = \
            flask.request.json['model_type'], \
            flask.request.json['params'], \
            flask.request.json['name'], \
            flask.request.json['values']

        model = mf.get_model(model_type, params)
        fitted_model = model.fit(*values)
        mm.add_model(name, fitted_model)
    except ValueError as e:
        return jsonify(message=str(e)), 400
    except ModuleNotFoundError as e:
        return jsonify(message=str(e)), 404

    return jsonify(message='OK'), 200


@app.route('/get_models')
def get_models():
    try:
        user = flask.request.args.get('user', None)
        if user:
            return jsonify(data=list(mm.get_models_for_user(user))), 200
        return jsonify(data=list(mm.get_models())), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400
    except ModuleNotFoundError as e:
        return jsonify(message=str(e)), 404
    except Exception as e:
        return jsonify(message=str(e)), 400
