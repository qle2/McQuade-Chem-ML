# import unittest
import pandas as pd
from core import models


class TestIngest:



    def test_load_smiles_dropfalse(self):
        """
        Test if ingest.py is returning a dataframe and a SMILES column when drop=False

        """
        model_test = models.MlModel('gdb', 'water-energy.csv', 'expt')
        # csv, smiles_col = load_smiles(model_test.data, "water-energy.csv", drop=False)
        # self.assertEqual(type(model_test.data), pd.DataFrame, 'Something is wrong, i can feel it')
        # self.assertEqual(type(model_test.smiles), pd.Series, 'Something is wrong, i can feel it')
        assert type(model_test.data) == pd.DataFrame
        assert type(model_test.smiles) == pd.Series

    def test_load_smiles_droptrue(self):
        """
        Test if ingest.py is returning a dataframe and a SMILES column when drop=True

        """
        model_test = models.MlModel('gdb', 'water-energy.csv', 'expt', drop=False)
        # csv, smiles_col = load_smiles(self, "water-energy.csv", drop=True)
        assert type(model_test.data) == pd.DataFrame
        assert type(model_test.smiles) == pd.Series