from DecisionTreeClassifier import DecisionTreeClassifier
from GradientBoostingClassifier import GradientBoostingClassifier


class ModelsFactory:

    @staticmethod
    def get_model(name, params):
        try:
            if name == 'DecisionTreeClassifier':
                return DecisionTreeClassifier(params)
            if name == 'GradientBoostingClassifier':
                return GradientBoostingClassifier(params)
        except Exception as e:
            raise ValueError(str(e))
        raise ValueError(f'There is no support of model {name} yet!')
