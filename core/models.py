'''
One way to handle the OOP of this code base is to handle each model as the instance of a class.
Required attributes will be what type of model and what data it uses.
Defaults will handle the splitting type, tuning etc.

Results of the model will be stored in the class instance,
for example you could have a model.pva be the pva graph and
model.results be the r2, rmse, time, etc.
'''
from core import grid, regressors, analysis, features, ingest
import csv
import subprocess
from pathlib import Path
import os
from main import *

class MlModel:
    def __init__(self, algorithm, dataset, target, drop=True):
        """Learning algorithm, dataset and target property's column name."""
        self.algorithm = algorithm
        self.dataset = dataset
        self.target = target
        self.data, self.smiles = ingest.load_smiles(self, dataset, drop)

    def featurization(self, feats=None):
        """ Featurizes molecules in dataset.
            Keyword arguments:
            feats -- Features you want.  Default = None (requires user input)
        """
        self.data, self.feat_meth, self.feat_time = features.featurize(self.data, self.algorithm, feats)



    def run(self, tune=False):
        """ Runs model. Returns log of results and graphs."""

        # store tune as attribute for cataloguing
        self.tuned = tune

        # Split data up. Set random seed here for graph comparison purposes.
        train_features, test_features, train_target, test_target, self.feature_list = features.targets_features(self.data, self.target, random=42)

        # set the model specific regressor function from sklearn
        self.regressor = regressors.regressor(self.algorithm)

        if tune:  # Do hyperparameter tuning

            # ask for tuning variables
            # folds = int(input('Please state the number of folds for hyperparameter searching: '))
            # iters = int(input('Please state the number of iterations for hyperparameter searching: '))
            # jobs = int(input('Input the number of processing cores to use. (-1) to use all.'))

            # FIXME Unfortunate hard code deep in the program.
            folds = 10
            iters = 5
            jobs = 30

            # Make parameter grid
            param_grid = grid.make_grid(self.algorithm)

            # Run Hyper Tuning
            params,  self.tuneTime = regressors.hyperTune(self.regressor(), train_features,
                                                          train_target, param_grid, folds, iters, jobs=jobs)

            # redefine regressor model with best parameters.
            self.regressor = self.regressor(**params)  # **dict will unpack a dictionary for use as keywrdargs

        else:  # Don't tune.
            self.regressor = self.regressor()  # make it callable to match Tune = True case
            self.tuneTime = None

        # Done tuning, time to fit and predict
        pva, fit_time = analysis.predict(self.regressor, train_features, test_features, train_target, test_target)

        #Variable importance for rf and gdb
        analysis.impgraph(self.regressor, train_features, train_target, self.feature_list)
        # test multipredict
        self.pvaM, fits_time = analysis.multipredict(self.regressor, train_features, test_features, train_target, test_target)
        self.graphM = analysis.pvaM_graphs(self.pvaM)
        # self.graph = analysis.pva_graphs(pva, self.algorithm)

        # run the model 5 times and collect the metric stats as dictionary
        self.stats = analysis.replicate_model(self, 5)

    def store(self):
        """  Organize and store model inputs and outputs.  """

        # move to root
        os.chdir(ROOT_DIR)

        # Check if output folder exists, create if not
        Path("./output").mkdir(parents=True, exist_ok=True)
        # move into output dir
        os.chdir('./output')



        # Check if model was tuned, store a string
        if self.tuned:
            tuned = 'tuned'
        else:
            tuned = 'notune'

        # unpack featurization method list
        feats = ''
        for meth in self.feat_meth:
            feats = feats + '-' + str(meth)
        # str(self.feat_meth)[1:-1]

        # create model file name
        name = self.dataset[:-4] + '-' + self.algorithm + feats + '-' + tuned
        csvfile = name + '.csv'

        # create dictionary of attributes
        att = dict(vars(self))  # makes copy so does not affect original attributes
        del att['data']  # do not want DF in dict
        del att['smiles']  # do not want series in dict
        del att['graphM']  # do not want graph object
        del att['stats']  # will unpack and add on
        att.update(self.stats)

        # Write contents of attributes dictionary to a CSV
        with open(csvfile, 'w') as f:  # Just use 'w' mode in 3.x
            w = csv.DictWriter(f, att.keys())
            w.writeheader()
            w.writerow(att)
            f.close()

        # save graphs
        self.graphM.savefig(name+'PvAM')
        self.graphM.close()  # close to conserve memory when running many models.
        # self.graph.savefig(name+'PvA')

        # make folders for each run
        # dirsp = 'mkdir ' + name  # str for bash command
        os.mkdir(name)
        # subprocess.Popen(dirsp.split(), stdout=subprocess.PIPE)  # run bash command

        # Move files to new folders
        movesp = 'mv ./' + name + '* ' + name + '/'
        subprocess.Popen(movesp, shell=True, stdout=subprocess.PIPE)  # run bash command




# # Initiate Model
# model1 = MlModel('rf', 'ESOL.csv', 'water-sol')
#
# # featurize data with rdkit2d
# model1.featurization([0])
# # print(model1.feat_meth)
#
#
# # Run the model with hyperparameter optimization
# model1.run(tune=False)
# # print('Tune Time:', model1.tuneTime)
#
#
#
# # Save results
# model1.store()
#
#
# # Must show() graph AFTER it has been saved.
# # if show() is called before save, the save will be blank
# # display PvA graph
# model1.graphM.show()

# # go home
# os.chdir(hte.ROOT_DIR)
#
# # Initiate Model
# model1 = MlModel('gdb', 'dataFiles/ESOL.csv', 'water-sol')
#
# # featurize data with rdkit2d
# model1.featurization([0])
# print(model1.feat_meth)
#
#
# # Run the model with hyperparameter optimization
# model1.run(tune=False)
# # print('Tune Time:', model1.tuneTime)
#
#
#
# # Save results
# model1.store()
#
#
# # Must show() graph AFTER it has been saved.
# # if show() is called before save, the save will be blank
# # display PvA graph
# model1.graphM.show()
#
