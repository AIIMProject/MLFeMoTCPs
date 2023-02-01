from Tools.DatasetTools.Commoms import * 
from sklearn.model_selection import train_test_split
from Tools.DatasetTools.MLConveniences import *
from itertools import product
from tqdm.auto import tqdm
import json

class ModelOptions:

    def  __init__(self, dataset):
        self._dataset = dataset
        self._resultslocation = os.path.join(dataset, 'results')
        self._modeloptions = {}
        self._modeloptionsfilename = {}

    @property
    def  dataset(self):
        return self._dataset

    @property
    def  resultslocation(self):
        return self._resultslocation

    @property
    def  modeloptions(self):
        return self._modeloptions

    @modeloptions.setter
    def modeloptions(self, value:dict[str, list]):
        self._modeloptions.update(value)

    @property
    def  modeloptionsfilename(self):
        return self._modeloptionsfilename

    @modeloptionsfilename.setter
    def  modeloptionsfilename(self, value:dict[str, list]):
        self._modeloptionsfilename.update(value)

    
    def load_model_options(self, modelname):
        self.modeloptionsfilename = {
                modelname: os.path.join(self.resultslocation, modelname+'_options.json')
                }
        if os.path.exists(self.modeloptionsfilename[modelname]):
            with open(self.modeloptionsfilename[modelname], 'r') as jsf:
                thismodeloptions = json.load(jsf)
        self.modeloptions = thismodeloptions

    def save_model_options(self, modelname, options:dict[str, list]):
        self.modeloptionsfilename = {
                modelname: os.path.join(self.resultslocation, modelname+'_options.json')
                }
        with open(self.modeloptionsfilename[modelname], 'w') as jsf:
            json.dump(options,jsf )

        self.modeloptions = options
