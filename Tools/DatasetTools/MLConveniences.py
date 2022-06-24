from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict, GridSearchCV
from math import sqrt
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR
from sklearn.inspection import permutation_importance
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import Lasso
from sklearn.neural_network import MLPRegressor

# other conveniences

def score_fitted_model(fittedmodel, xtrain,  xtest, ytrain,ytest):
    predict_train = fittedmodel.predict(xtrain)
    predict_test = fittedmodel.predict(xtest)
    return {'test': mean_squared_error(ytest, predict_test, squared = False), 'train':mean_squared_error(ytrain, predict_train, squared = False)}


