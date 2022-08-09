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
        print(self.DS.StrucNames)


    def test_splits_vs_rs(self):
        Splits = {rs: self.DS.get_samplesplit(split_random_state=rs) for rs in self.Tester.RandomStates}
        BS_test = {thisrs: self.DS.BS.loc[thissplit['test']] for thisrs, thissplit  in Splits.items()}
        Structures_test = {thisrs: Featurizer(thisbs).StrucNames for thisrs, thisbs in BS_test.items()}
        fig, axes = plt.subplots(1,len(Splits), sharey = True)
        for ax, ( thisrs, thisnames ) in zip(axes, Structures_test.items()):
            ax.hist(thisnames, orientation='horizontal')
            ax.yaxis.set_tick_params(labelleft=True)
        plt.savefig('populations.pdf')

        





if __name__ == '__main__':
    unittest.main()


