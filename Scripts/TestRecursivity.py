import unittest
import sys
import os
currentlocation = os.path.dirname(__file__)
sys.path.insert(0, currentlocation)
import Recursivity as mod


class TestRecursivity(unittest.TestCase):

    @classmethod
    def setUp():
        pass

    def test_an_selection(self):
        print(mod.X)


    
