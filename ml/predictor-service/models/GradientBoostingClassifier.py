from AbstractClassifier import AbstractClassifier
from sklearn.ensemble import GradientBoostingClassifier as GBClassifier


class GradientBoostingClassifier(AbstractClassifier):

    def __init__(self, params=None):
        super().__init__()
        if params is None:
            params = {}
        self.model = GBClassifier(**params)
