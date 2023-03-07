import mlflow.sklearn
from mlflow.tracking import MlflowClient
import mlflow.pyfunc

PATH = 'storage/models'


class ModelsManager:

    def __init__(self):
        mlflow.set_tracking_uri('http://host.docker.internal:5000')
        self.client = MlflowClient()

    @staticmethod
    def add_model(name, model, model_type=None, params=None):
        mlflow.sklearn.log_model(model, name, registered_model_name=name)

    def get_model(self, name):
        self._validate_name(name)
        latest_version = self.client.get_registered_model(name)\
            .latest_versions[0].version

        model = mlflow.pyfunc.load_model(model_uri=f'models:/{name}/{latest_version}')

        return model

    def delete_model(self, name):
        if name in self.get_models():
            self.client.delete_registered_model(name)

    def _validate_name(self, name):
        if name not in self.get_models():
            raise ValueError(f'There is no model "{name}"!')

    def get_models(self):
        return list(map(lambda x: x.name, self.client.list_registered_models()))

    def get_models_for_user(self, name):
        by_user = filter(lambda x: x.startswith(name + '_'), self.get_models())
        return list(map(lambda x: x.replace(name + '_', ''), by_user))
