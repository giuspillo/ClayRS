from abc import ABC
from typing import Union

import numpy as np
from scipy import sparse
from sklearn.linear_model._base import LinearModel as SKLinearModel
from sklearn.linear_model._stochastic_gradient import BaseSGDRegressor

from sklearn.linear_model import LinearRegression, BayesianRidge, Ridge, SGDRegressor, ARDRegression, \
    HuberRegressor, PassiveAggressiveRegressor


class Regressor(ABC):
    """
    Abstract class for Regressors
    """

    def __init__(self, model: Union[SKLinearModel, BaseSGDRegressor]):
        self.__model = model

    @property
    def model(self):
        return self.__model

    def fit(self, X: list, Y: list = None):
        """
        Fit the regressor.
        First the classifier is instantiated, then we transform the Training Data,
        then the actual fitting is done.

        Training data (X) is in the form:
            X = [ (merged) representation for item 1, (merged) representation for item 2, ...]
        where every item is a representation for an item (can be a merged one in case multiple representations
        are chosen)

        Target data (Y) is in the form:
            Y = [0, 1, ... ]
        where 0 represent a negative item, 1 represent a positive item

        Args:
            X (list): list containing Training data.
            Y (list): list containing Training targets.
        """
        self.__model = self.__model.fit(X, Y)

    def predict(self, X_pred: list):
        """
        Predicts the probability for every item in X_pred.
        It uses the method predict() from sklearn of the instantiated regressor

        It's in the form:
            X_pred = [ (merged) representation for item 1, (merged) representation for item 2, ...]
        where every item is a representation for an item (can be a merged one in case multiple representations
        are chosen)

        Args:
            X_pred (list): list containing data to predict.
        """
        return self.__model.predict(X_pred)


class SkLinearRegression(Regressor):
    """
    Class that implements the LinearRegression regressor from sklearn.
    The parameters one could pass are the same ones you would pass instantiating
    the regressor LinearRegression directly from sklearn.
    """

    def __init__(self, *args, **kwargs):
        model = LinearRegression(*args, **kwargs)

        super().__init__(model)

    def __str__(self):
        return "SkLinearRegression"


class SkRidge(Regressor):
    """
    Class that implements the Ridge regressor from sklearn.
    The parameters one could pass are the same ones you would pass instantiating
    the regressor Ridge directly from sklearn.
    """
    def __init__(self, *args, **kwargs):
        model = Ridge(*args, **kwargs)

        super().__init__(model)

    def fit(self, X: Union[np.ndarray, sparse.csr_matrix], Y: list = None):
        self.model.fit(X.toarray() if isinstance(X, sparse.csr_matrix) else X, Y)

    def predict(self, X_pred: Union[np.ndarray, sparse.csr_matrix]):
        return self.model.predict(X_pred.toarray() if isinstance(X_pred, sparse.csr_matrix) else X_pred)

    def __str__(self):
        return "SkRidge"


class SkBayesianRidge(Regressor):
    """
    Class that implements the BayesianRidge regressor from sklearn.
    The parameters one could pass are the same ones you would pass instantiating
    the regressor BayesianRidge directly from sklearn.
    """
    def __init__(self, *args, **kwargs):
        model = BayesianRidge(*args, **kwargs)

        super().__init__(model)

    def fit(self, X: Union[np.ndarray, sparse.csr_matrix], Y: list = None):
        self.model.fit(X.toarray() if isinstance(X, sparse.csr_matrix) else X, Y)

    def predict(self, X_pred: Union[np.ndarray, sparse.csr_matrix]):
        return self.model.predict(X_pred.toarray() if isinstance(X_pred, sparse.csr_matrix) else X_pred)

    def __str__(self):
        return "SkBayesianRidge"


class SkSGDRegressor(Regressor):
    """
    Class that implements the SGD regressor from sklearn.
    The parameters one could pass are the same ones you would pass instantiating
    the regressor SGD directly from sklearn.
    """
    def __init__(self, *args, **kwargs):
        model = SGDRegressor(*args, **kwargs)
        super().__init__(model)

    def __str__(self):
        return "SkSGDRegressor"


class SkARDRegression(Regressor):
    """
    Class that implements the ARD regressor from sklearn.
    The parameters one could pass are the same ones you would pass instantiating
    the regressor ARD directly from sklearn.
    """
    def __init__(self, *args, **kwargs):

        model = ARDRegression(*args, **kwargs)
        super().__init__(model)

    def fit(self, X: Union[np.ndarray, sparse.csr_matrix], Y: list = None):
        self.model.fit(X.toarray() if isinstance(X, sparse.csr_matrix) else X, Y)

    def predict(self, X_pred: Union[np.ndarray, sparse.csr_matrix]):
        return self.model.predict(X_pred.toarray() if isinstance(X_pred, sparse.csr_matrix) else X_pred)

    def __str__(self):
        return "SkARDRegression"


class SkHuberRegressor(Regressor):
    """
    Class that implements the Huber regressor from sklearn.
    The parameters one could pass are the same ones you would pass instantiating
    the regressor Huber directly from sklearn.
    """
    def __init__(self, *args, **kwargs):

        model = HuberRegressor(*args, **kwargs)
        super().__init__(model)

    def __str__(self):
        return "SkHuberRegressor"


class SkPassiveAggressiveRegressor(Regressor):
    """
    Class that implements the PassiveAggressive regressor from sklearn.
    The parameters one could pass are the same ones you would pass instantiating
    the regressor PassiveAggressive directly from sklearn.
    """
    def __init__(self, *args, **kwargs):

        model = PassiveAggressiveRegressor(*args, **kwargs)
        super().__init__(model)

    def __str__(self):
        return "SkPassiveAggressiveRegressor"