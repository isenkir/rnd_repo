from AbstractClassifier import AbstractClassifier
from sklearn.tree import DecisionTreeClassifier as DTClassifier


class DecisionTreeClassifier(AbstractClassifier):

    def __init__(self, params=None):
        super().__init__()
        if params is None:
            params = {}
        self.model = DTClassifier(**params)
