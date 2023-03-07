class AbstractClassifier:

    def __init__(self):
        self.model = None

    def predict(self, X):
        try:
            return self.model.predict(X)
        except Exception as e:
            raise ValueError(str(e))

    def fit(self, X, y):
        try:
            return self.model.fit(X, y)
        except Exception as e:
            raise ValueError(str(e))
