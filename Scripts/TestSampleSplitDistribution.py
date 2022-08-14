import unittest
import sys
import os
currentlocation = os.path.dirname(__file__)
projectroot = os.path.dirname(currentlocation)
sys.path.insert(0, currentlocation)
sys.path.insert(1, projectroot)
sys.path.insert(2, '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer')

from Tools.DatasetTools.Commoms import *

from BopFoxFeaturizer.Featurizer import Featurizer

from Tools.DatasetTools.DatasetOperator import Dataset, DatasetTester

dataset = 'Fe-Mo'

class TestPerformanceVsRs(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.DS = Dataset(dataset)
        cls.Tester = DatasetTester()

    def test_bs_strucs(self):
        print(self.DS.StructureNames)


    def test_splits_vs_rs(self):
        Splits = {rs: self.DS.get_samplesplit(split_random_state=rs) for rs in self.Tester.RandomStates}
        BS_test = {thisrs: self.DS.BS.loc[thissplit['test']] for thisrs, thissplit  in Splits.items()}
        BS_train = {thisrs: self.DS.BS.loc[thissplit['train']] for thisrs, thissplit  in Splits.items()}
        Structures_test = {thisrs: thisbs['Phase'] for thisrs, thisbs in BS_test.items()}
        Structures_train = {thisrs: thisbs['Phase'] for thisrs, thisbs in BS_train.items()}
        fig, axes = plt.subplots(1,len(Splits), sharey = True)
        for ax, ( thisrs, thisnames ) in zip(axes, Structures_train.items()):
            sns.histplot(y=thisnames, discrete=True, ax=ax )
#            ax.hist(thisnames, orientation='horizontal')
        for ax, ( thisrs, thisnames ) in zip(axes, Structures_test.items()):
            sns.histplot(y=thisnames, discrete=True, ax=ax )
            #ax.hist(thisnames, orientation='horizontal')
        fig.supxlabel('Counts')
        plt.savefig('populations.pdf')

    def test_folds(self):
        folds = self.DS.get_folds()
        nfolds = self.DS.nfolds
        fig, axes = plt.subplots(1, self.DS.nfolds, sharey=True)
        for ax, fold in zip(axes, folds):
            trainsplit = self.DS.allindex[fold[0]]
            testsplit = self.DS.allindex[fold[1]]
            sns.histplot(y=self.DS.StructureNames.loc[trainsplit], ax = ax)
            sns.histplot(y=self.DS.StructureNames.loc[testsplit], ax = ax, color='tomato')
        fig.savefig('fold_populations.pdf')

        

        





if __name__ == '__main__':
    unittest.main()


