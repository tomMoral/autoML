#!/usr/bin/env python

##############################
# ChaLearn AutoML challenge  #
# April 22 hackathon version #
##############################

# Usage: python run.py input_dir output_dir

# This sample code can be used either 
# - to submit RESULTS depostited in the res/ subdirectory or 
# - as a template for CODE submission.
#
# The input directory input_dir contains 5 subdirectories named by dataset,
# including:
#   dataname/dataname_feat.type          -- the feature type "Numerical", "Binary", or "Categorical" (Note: if this file is abscent, get the feature type from the dataname.info file)
#   dataname/dataname_public.info        -- parameters of the data and task, including metric and time_budget
#   dataname/dataname_test.data          -- training, validation and test data (solutions/target values are given for training data only)
#   dataname/dataname_train.data
#   dataname/dataname_train.solution
#   dataname/dataname_valid.data
#
# The output directory will receive the predicted values (no subdirectories):
#   dataname_test_000.predict            -- Provide predictions at regular intervals to make sure you get some results even if the program crashes
#   dataname_test_001.predict
#   dataname_test_002.predict
#   ...
#   dataname_valid_000.predict
#   dataname_valid_001.predict
#   dataname_valid_002.predict
#   ...
# 
# Result submission:
# =================
# Search for @RESULT to locate that part of the code.
# ** Always keep this code. **
# If the subdirectory res/ contains result files (predicted values)
# the code just copies them to the output and does not train/test models.
# If no results are found, a model is trained and tested (see code submission).
#
# Code submission:
# ===============
# Search for @CODE to locate that part of the code.
# ** You may keep or modify this template or subtitute your own code. **
# The program saves predictions regularly. This way the program produces
# at least some results if it dies (or is terminated) prematurely. 
# This also allows us to plot learning curves. The last result is used by the
# scoring program.
# We implemented 2 classes:
# 1) DATA LOADING:
#    ------------
# Use/modify 
#                  D = DataManager(basename, input_dir, ...) 
# to load and preprocess data.
#     Missing values --
#       Our default method for replacing missing values is trivial: they are replaced by 0.
#       We also add extra indicator features where missing values occurred. This doubles the number of features.
#     Categorical variables --
#       The location of potential Categorical variable is indicated in D.feat_type.
#       NOTHING special is done about them in this sample code. 
#     Feature selection --
#       We only implemented an ad hoc feature selection filter efficient for the 
#       dorothea dataset to show that performance improves significantly 
#       with that filter. It takes effect only for binary classification problems with sparse
#       matrices as input and unbalanced classes.
# 2) LEARNING MACHINE:
#    ----------------
# This is from the original sample code IGNORE... it has been replaced by simpler code by Lukasz Romaszzko
# ------------------------------------------------------------------------------------------------------
# Use/modify 
#                 M = MyAutoML(D.info, ...) 
# to create a model.
#     Number of base estimators --
#       Our models are ensembles. Adding more estimators may improve their accuracy.
#       Use M.model.n_estimators = num
#     Training --
#       M.fit(D.data['X_train'], D.data['Y_train'])
#       Fit the parameters and hyper-parameters (all inclusive!)
#       What we implemented hard-codes hyper-parameters, you probably want to
#       optimize them. Also, we made a somewhat arbitrary choice of models in
#       for the various types of data, just to give some baseline results.
#       You probably want to do better model selection and/or add your own models.
#     Testing --
#       Y_valid = M.predict(D.data['X_valid'])
#       Y_test = M.predict(D.data['X_test']) 
#
# ALL INFORMATION, SOFTWARE, DOCUMENTATION, AND DATA ARE PROVIDED "AS-IS". 
# ISABELLE GUYON, CHALEARN, AND/OR OTHER ORGANIZERS OR CODE AUTHORS DISCLAIM
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY PARTICULAR PURPOSE, AND THE
# WARRANTY OF NON-INFRIGEMENT OF ANY THIRD PARTY'S INTELLECTUAL PROPERTY RIGHTS. 
# IN NO EVENT SHALL ISABELLE GUYON AND/OR OTHER ORGANIZERS BE LIABLE FOR ANY SPECIAL, 
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF SOFTWARE, DOCUMENTS, MATERIALS, 
# PUBLICATIONS, OR INFORMATION MADE AVAILABLE FOR THE CHALLENGE. 
#
# Main contributors: Isabelle Guyon and Arthur Pesah, March-October 2014
# Lukasz Romasco April 2015
# Originally inspired by code code: Ben Hamner, Kaggle, March 2013
# Modified by Ivan Judson and Christophe Poulain, Microsoft, December 2013

# =========================== BEGIN USER OPTIONS ==============================
# Verbose mode: 
##############
# Recommended to keep verbose = True: shows various progression messages
verbose = True # outputs messages to stdout and stderr for debug purposes

# Debug level:
############## 
# 0: run the code normally, using the time budget of the tasks
# 1: run the code normally, but limits the time to max_time
# 2: run everything, but do not train, generate random outputs in max_time
# 3: stop before the loop on datasets
# 4: just list the directories and program version
debug_mode = 0

# Time budget
#############
# Maximum time of training in seconds PER DATASET (there are 5 datasets). 
# The code should keep track of time spent and NOT exceed the time limit 
# in the dataset "info" file, stored in D.info['time_budget'], see code below.
# If debug >=1, you can decrease the maximum time (in sec) with this variable:
max_time = 90

# Maximum number of cycles
##########################
# Your training algorithm may be fast, so you may want to limit anyways the 
# number of points on your learning curve (this is on a log scale, so each 
# point uses twice as many time than the previous one.)
max_cycle = 1 # Use 1 here for the new starting kit

# ZIP your code
###############
# You can create a code submission archive, ready to submit, with zipme = True.
# This is meant to be used on your LOCAL server.
import datetime
zipme = True # use this flag to enable zipping of your code submission
the_date = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
submission_filename = '../automl_sample_submission_' + the_date # Put the submission file one level up

# I/O defaults
##############
# Use default location for the input and output data:
# If no arguments to run.py are provided, this is where the data will be found
# and the results written to. Change the root_dir to your local directory.
root_dir = "../"
default_input_dir = root_dir + "data" # here it accepts the mother data directory or any subdirectory, e.g. "Data01/adult"
default_output_dir = "res"

# =========================== END USER OPTIONS ================================

# Version of the sample code
# Change in 1.1: time is measured by time.time(), not time.clock(): we keep track of wall time
version = 2.0 

# General purpose functions
import os
from sys import argv, path
import numpy as np
import time
overall_start = time.time()
from sklearn.ensemble import RandomForestClassifier as RForestClass
from sklearn.ensemble import RandomForestRegressor as RForestRegress
from sklearn.ensemble import BaggingClassifier, BaggingRegressor
from sklearn.naive_bayes import BernoulliNB
# Our directories
# Note: On cadalab, there is an extra sub-directory called "program"
running_on_codalab = False
run_dir = os.path.abspath(".")
codalab_run_dir = os.path.join(run_dir, "program")
if os.path.isdir(codalab_run_dir):
    run_dir=codalab_run_dir
    running_on_codalab = True
    print "Running on Codalab!"
lib_dir = os.path.join(run_dir, "lib")
res_dir = os.path.join(run_dir, "res")

# Our libraries
path.append (run_dir)
path.append (lib_dir)
import data_io                       # general purpose input/output functions
from data_io import vprint           # print only in verbose mode
from data_manager import DataManager # load/save data and get info about them
from models import MyAutoML          # example model from scikit learn (unused in this version)

from sklearn.cross_validation import *

if debug_mode >= 4 or running_on_codalab: # Show library version and directory structure
    data_io.show_version()
    data_io.show_dir(run_dir)

# =========================== BEGIN PROGRAM ================================

if __name__=="__main__" and debug_mode<4:   
    #### Check whether everything went well (no time exceeded)
    execution_success = True
    
    #### INPUT/OUTPUT: Get input and output directory names
    if len(argv)==1: # Use the default input and output directories if no arguments are provided
        input_dir = default_input_dir
        output_dir = default_output_dir
    else:
        input_dir = argv[1]
        output_dir = os.path.abspath(argv[2])
    # Move old results and create a new output directory
    if not(running_on_codalab):
        data_io.mvdir(output_dir, '../'+output_dir+'_'+the_date)
    data_io.mkdir(output_dir)

    #### INVENTORY DATA (and sort dataset names alphabetically)
    datanames = data_io.inventory_data(input_dir)

    #### DEBUG MODE: Show dataset list and STOP
    if debug_mode>=3:
        data_io.show_io(input_dir, output_dir)
        print('\n****** Sample code version ' + str(version) + ' ******\n\n' + '========== DATASETS ==========\n')
        data_io.write_list(datanames)      
        datanames = [] # Do not proceed with learning and testing

    # ==================== @RESULT SUBMISSION (KEEP THIS) =====================
    # Always keep this code to enable result submission of pre-calculated results
    # deposited in the res/ subdirectory.
    if len(datanames)>0:
        vprint( verbose,  "************************************************************************")
        vprint( verbose,  "****** Attempting to copy files (from res/) for RESULT submission ******")
        vprint( verbose,  "************************************************************************")
        OK = data_io.copy_results(datanames, res_dir, output_dir, verbose) # DO NOT REMOVE!
        if OK: 
            vprint( verbose,  "[+] Success")
            datanames = [] # Do not proceed with learning and testing
        else:
            vprint( verbose, "======== Some missing results on current datasets!")
            vprint( verbose, "======== Proceeding to train/test:\n")
    # =================== End @RESULT SUBMISSION (KEEP THIS) ==================

    # ================ @CODE SUBMISSION (SUBTITUTE YOUR CODE) ================= 
    overall_time_budget = 0
    for basename in datanames: # Loop over datasets
        
        vprint( verbose,  "************************************************")
        vprint( verbose,  "******** Processing dataset " + basename.capitalize() + " ********")
        vprint( verbose,  "************************************************")

        # ======== Learning on a time budget:
        # Keep track of time not to exceed your time budget. Time spent to inventory data neglected.
        start = time.time()

        # ======== Creating a data object with data, informations about it
        vprint( verbose,  "======== Reading and converting data ==========")
        D = DataManager(basename, input_dir, replace_missing=True, filter_features=True, verbose=verbose)
        print D

        # ======== Keeping track of time
        if debug_mode < 1:
            time_budget = D.info['time_budget']   # <== HERE IS THE TIME BUDGET!
        else:
            time_budget = max_time
        overall_time_budget = overall_time_budget + time_budget
        time_spent = time.time() - start
        vprint( verbose,  "[+] Remaining time after reading data %5.2f sec" % (time_budget-time_spent))
        if time_spent >= time_budget:
            vprint( verbose,  "[-] Sorry, time budget exceeded, skipping this task")
            execution_success = False
            continue

        # ========= Creating a model, knowing its assigned task from D.info['task'].
        # The model can also select its hyper-parameters based on other elements of info.  
        # vprint( verbose,  "======== Creating model ==========")
        # M = MyAutoML(D.info, verbose, debug_mode)
        # print M
        # The code above corresponds to the original starting kit

        # ========= Iterating over learning cycles and keeping track of time
        time_spent = time.time() - start
        vprint( verbose,  "[+] Remaining time after building model %5.2f sec" % (time_budget-time_spent))
        if time_spent >= time_budget:
            vprint( verbose,  "[-] Sorry, time budget exceeded, skipping this task")
            execution_success = False
            continue

        time_budget = time_budget - time_spent # Remove time spent so far
        start = time.time()              # Reset the counter
        time_spent = 0                   # Initialize time spent learning
        time_spent_last = 0              # Initialize time spent learning
        cycle = 0
        
        while  cycle <= 1: # max_cycle: # In this version max_cycle = 1
            begin = time.time()
            vprint( verbose,  "=========== " + basename.capitalize() +" Training cycle " + str(cycle) +" ================") 
            n_estimators = 50 # In clycle 0 we try with just 50 estimators to probe the duration
            if cycle==1:
                n_estimators = int((np.floor(time_budget / time_spent_last) - 1 ) * 50) # In the next cycle we use the remaining time
                if n_estimators <=0: break # IG
            vprint( verbose,  "[+] Number of estimators: %d" % (n_estimators))   
            
            K = D.info['target_num']
            sparse = False
            if D.info['is_sparse'] == 1:
                sparse = True

            task = D.info['task']
            seed = 1 # seend for the random number generator
            X_train = D.data['X_train']
            y_train = D.data['Y_train']
            print(D.data.keys())

            nb_parallel = 6
            x_local_train, x_local_valid, y_local_train, y_local_valid = train_test_split(D.data['X_train'], D.data['Y_train'], test_size=0.2, random_state=1)

            if task == 'binary.classification' or task == 'multiclass.classification':
                if sparse:
                    M = BaggingClassifier(base_estimator=BernoulliNB(), n_estimators=n_estimators/10, random_state=1, n_jobs=nb_parallel).fit(x_local_train, y_local_train)
                else:
                    M = RForestClass(n_estimators, random_state=1).fit(x_local_train, y_local_train)
            elif task == 'multilabel.clmetric_typeassification':
                if sparse:
                    Ms = [BaggingClassifier(base_estimator=BernoulliNB(), n_estimators=n_estimators/10, random_state=1, n_jobs=nb_parallel).fit(x_local_train, y_local_train[:, i]) for i in range(K)]
                else:
                    Ms = [RForestClass(n_estimators, random_state=1).fit(x_local_train, y_local_train[:, i]) for i in range(K)]
            elif task == 'regression':  
                if sparse:
                    M = BaggingRegressor(base_estimator=BernoulliNB(), n_estimators=n_estimators/10, random_state=1, n_jobs=nb_parallel).fit(x_local_train, y_local_train)
                else:            
                    M = RForestRegress(n_estimators, random_state=1, n_jobs=nb_parallel).fit(x_local_train, y_local_train)
            else:
                vprint( verbose,  "[-] task not recognized")
                break         
            vprint( verbose,  "[+] Fitting success, time spent so far %5.2f sec" % (time.time() - start))
                
            # Make predictions on local validation set
            if task == 'binary.classification':
                y_local_valid_pred = M.predict_proba(x_local_valid)[:, 1]
            elif task == 'multiclass.classification':
                y_local_valid_pred = np.array([M.predict_proba(x_local_valid)[:, i] for i in range(K)]).T 
            elif task == 'multilabel.classification':
                y_local_valid_pred = np.array([Ms[i].predict_proba(x_local_valid)[:, 1] for i in range(K)]).T
            elif task == 'regression':
                y_local_valid_pred = M.predict(x_local_valid)
            
   
            # Local validation
            # x_local_valid, y_local_valid 
            metric_type = D.info['metric']            
            if 'f1_metric' == metric_type:
                vprint(verbose, 'f1_metric')
            elif 'r2_metric' == metric_type:
                vprint(verbose, 'r2_metric')
            elif 'bac_metric' == metric_type:
                vprint(verbose, 'bac_metric')
            elif 'auc_metric' == metric_type:
                vprint(verbose, 'auc_metric')
            elif 'pac_metric' == metric_type:
                vprint(verbose, 'pac_metric')
            else:
                vprint(verbose, 'What ?!')            

            
            
            # Make predictions
            if task == 'binary.classification':
                Y_valid = M.predict_proba(D.data['X_valid'])[:, 1]
                Y_test =  M.predict_proba(D.data['X_test'])[:, 1]
            elif task == 'multiclass.classification':
                Y_valid = np.array([M.predict_proba(D.data['X_valid'])[:, i] for i in range(K)]).T 
                Y_test =  np.array([M.predict_proba(D.data['X_test'])[:, i] for i in range(K)]).T 
            elif task == 'multilabel.classification':
                Y_valid = np.array([Ms[i].predict_proba(D.data['X_valid'])[:, 1] for i in range(K)]).T
                Y_test =  np.array([Ms[i].predict_proba(D.data['X_valid'])[:, 1] for i in range(K)]).T
            elif task == 'regression':    
                Y_valid = M.predict(D.data['X_valid'])
                Y_test = M.predict(D.data['X_test'])
            
            
            if task == 'multilabel.classification' or task == 'multiclass.classification':
                if sparse:
                    eps = 0.001
                    for i in range(len(Y_valid)):
                        pos = np.argmax(Y_valid[i])
                        Y_valid[i] += eps
                        Y_valid[i][pos] -= K * eps
                    for i in range(len(Y_test)):
                        pos = np.argmax(Y_test[i])
                        Y_test[i] += eps
                        Y_test[i][pos] -= K * eps
                    
            
            vprint( verbose,  "[+] Prediction success, time spent so far %5.2f sec" % (time.time() - start))
            # Write results
            filename_valid = basename + '_valid_' + str(cycle).zfill(3) + '.predict'
            data_io.write(os.path.join(output_dir,filename_valid), Y_valid)
            filename_test = basename + '_test_' + str(cycle).zfill(3) + '.predict'
            data_io.write(os.path.join(output_dir,filename_test), Y_test)
            vprint( verbose,  "[+] Results saved, time spent so far %5.2f sec" % (time.time() - start))         
            time_spent = time.time() - start 
            vprint( verbose,  "[+] End cycle, remaining time %5.2f sec" % (time_budget-time_spent))
            cycle += 1
            time_spent_last = time.time() - begin
            time_budget = time_budget - time_spent_last # Remove time spent so far
            
    if zipme and not(running_on_codalab):
        vprint( verbose,  "========= Zipping this directory to prepare for submit ==============")
        data_io.zipdir(submission_filename + '.zip', ".")
        
    overall_time_spent = time.time() - overall_start
    if execution_success:
        vprint( verbose,  "[+] Done")
        vprint( verbose,  "[+] Overall time spent %5.2f sec " % overall_time_spent + "::  Overall time budget %5.2f sec" % overall_time_budget)
    else:
        vprint( verbose,  "[-] Done, but some tasks aborted because time limit exceeded")
        vprint( verbose,  "[-] Overall time spent %5.2f sec " % overall_time_spent + " > Overall time budget %5.2f sec" % overall_time_budget)
              
    if running_on_codalab: 
        if execution_success:
            exit(0)
        else:
            exit(1)


