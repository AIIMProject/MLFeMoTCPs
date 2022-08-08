import unittest
import sys
import os
currentlocation = os.path.dirname(__file__)
projectroot = os.path.dirname(currentlocation)
sys.path.insert(0, currentlocation)
sys.path.insert(1, projectroot)
from Tools.DatasetTools.DatasetOperator import Dataset, DatasetTester

dataset = 'Fe-Mo'



class TestPerformanceVsRs(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.DS = Dataset(dataset)
        cls.Tester = DatasetTester()

    def test_scores_vs_rs(self):
        scores_rs = self.Tester.learn_vs_split_rs(self.DS)
        self.assertGreater(len(scores_rs), 0)
        print(scores_rs)





if __name__ == '__main__':
    unittest.main()


