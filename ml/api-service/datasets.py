from sklearn.datasets import make_classification
import pickle
from os import listdir
import numpy as np

PATH = 'storage/datasets'


class DatasetManager:

    def __init__(self):
        self.add_dataset('test1', *self._get_random_dataset(), self._get_random_dataset()[0])
        self.add_dataset('test2', *self._get_random_dataset(), self._get_random_dataset()[0])
        self.add_dataset('test3', *self._get_random_dataset(), self._get_random_dataset()[0])

    @staticmethod
    def _get_random_dataset():
        X, y = make_classification(n_classes=2, n_features=10, n_samples=100)
        return X.tolist(), y.tolist()

    @staticmethod
    def _validate_df(X_train, y_train, X_test):
        try:
            X_tr = np.array(X_train)
            y_tr = np.array(y_train)
            X_t = np.array(X_test)
            if X_tr.shape[1] != X_t.shape[1]:
                raise ValueError('Train and test have different number of features!')
            if X_tr.shape[0] == 0:
                raise ValueError('Train has 0 not-null objects')
            if X_tr.shape[0] != y_tr.shape[0]:
                raise ValueError('X_train and y_train have different shapes!')
            if len(y_train) != y_tr.size:
                raise ValueError('y_train should be a simple list of integers!')
            if X_tr.dtype.kind not in ['i', 'u', 'f'] \
                    or y_tr.dtype.kind not in ['i', 'u', 'f'] \
                    or X_t.dtype.kind not in ['i', 'u', 'f']:
                raise ValueError('Data contains non-numeric values!')
        except Exception as e:
            raise ValueError(str(e))

    def add_dataset(self, name, X_train, y_train, X_test):
        self._validate_df(X_train, y_train, X_test)
        data = {
            'X_train': X_train,
            'y_train': y_train,
            'X_test': X_test
        }

        with open(f'{PATH}/{name}.pickle', 'wb') as f:
            pickle.dump(data, f)

    def _validate_name(self, name):
        if name not in self.get_datasets():
            raise ValueError(f'There is no dataset "{name}"!')

    @staticmethod
    def get_datasets():
        datasets = filter(lambda x: x.endswith('.pickle'), listdir(PATH))
        return list(map(lambda x: x.replace('.pickle', ''), datasets))

    def get_train(self, name):
        self._validate_name(name)
        with open(f'{PATH}/{name}.pickle', 'rb') as f:
            df = pickle.load(f)
        return df['X_train'], df['y_train']

    def get_test(self, name):
        self._validate_name(name)

        with open(f'{PATH}/{name}.pickle', 'rb') as f:
            df = pickle.load(f)
        return df['X_test']
