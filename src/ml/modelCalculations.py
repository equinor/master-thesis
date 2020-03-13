import sys, os
ROOT_PATH = os.path.abspath(".").split("src")[0]
module_path = os.path.abspath(os.path.join(ROOT_PATH+"/src/utils/"))
if module_path not in sys.path:
    sys.path.append(module_path)
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

import utilities
import plots
import metrics
import inspect
from src.ml.analysis.covmat import (covmat, printCovMat)
from src.ml.analysis.pca import (pca, printExplainedVarianceRatio)
from utilities import Args
from models import (
    kerasSequentialRegressionModel,
    kerasSequentialRegressionModelWithRegularization,
    sklearnMLP,
    sklearnLinear,
    sklearnRidgeCV,
    ensembleModel,
    kerasLSTMSingleLayerLeaky
)
from configs import (getConfig)

import matplotlib.pyplot as plt

args = Args({
    'activation': 'relu',
    'loss': 'mean_squared_error',
    'optimizer': 'adam',
    'metrics': ['mean_squared_error'],
    'epochs': 4000,
    'batchSize': 32,
    'verbose': 1,
    'callbacks': utilities.getBasicCallbacks(),
    'enrolWindow': None,
    'validationSize': 0.2,
    'testSize': 0.2
})

lstmArgs = Args({
    'activation': 'relu',
    'loss': 'mean_squared_error',
    'optimizer': 'adam',
    'metrics': ['mean_squared_error'],
    'epochs': 4000,
    'batchSize': 32,
    'verbose': 1,
    'callbacks': utilities.getBasicCallbacks(monitor="loss"),
    'enrolWindow': 1,
    'validationSize': 0.2,
    'testSize': 0.2
})

def main(filename, targetColumns):
    subdir = filename.split('/')[-2]
    columns, relevantColumns, labelNames, columnUnits, timestamps = getConfig(subdir)

    traintime, testtime, validtime = timestamps

    df = utilities.readDataFile(filename)
    df = utilities.getDataWithTimeIndex(df)
    df = df.dropna()

    if relevantColumns is not None:
        df = utilities.dropIrrelevantColumns(df, [relevantColumns, labelNames])

    df_train, df_test = utilities.getTestTrainSplit(df, traintime, testtime)
    X_train, y_train, X_test, y_test = utilities.getFeatureTargetSplit(df_train, df_test, targetColumns)

    keras_seq_mod_regl = kerasSequentialRegressionModelWithRegularization(
        X_train,
        y_train,
        args,
        [
            [50, args.activation],
            [20, args.activation]
        ],
    )
    keras_seq_mod_simple = kerasSequentialRegressionModel(
        X_train,
        y_train,
        args,
        [
            [20, args.activation]
        ],
    )
    keras_seq_mod_v_simple = kerasSequentialRegressionModel(
        X_train,
        y_train,
        args,
        [
            [X_train.shape[1], args.activation]
        ], 
    )
    keras_seq_mod = kerasSequentialRegressionModel(
        X_train,
        y_train,
        args,
        [
            [50, args.activation],
            [20, args.activation]
        ]
    )
    ensemble = ensembleModel(
        [
            keras_seq_mod_regl,
            #keras_seq_mod_simple,
            sklearnRidgeCV(X_train, y_train)
        ],
        X_train,
        y_train
    )
    lstmModel = kerasLSTMSingleLayerLeaky(
        X_train,
        y_train,
        lstmArgs,
        units=128,
        dropout=0.1,
        alpha=0.5
    )

    modelsList = [
        [keras_seq_mod, "MLP normal"],
        #[ensemble, "ensemble"],
        [lstmModel, 'lstm'],
        #[keras_seq_mod_regl, "MLP regularized"],
        #[keras_seq_mod_simple, "MLP simple"],
        #[keras_seq_mod_v_simple, "MLP very simple"],
        #[r1, "1.0 regulariation"],
        #[r4, "0.001"],
        #[r5, "0.0001"],
        #[sklearnLinear(X_train, y_train), "linear"],
        [sklearnRidgeCV(X_train, y_train), "ridge"],
    ]

    names, r2_train, r2_test, deviationsList, columnsList = utilities.predictWithModels(modelsList, X_train, y_train, X_test, y_test, targetColumns)
    #utilities.printModelPredictions(names, r2_train, r2_test)
    utilities.plotModelPredictions(plt, deviationsList, columnsList, df_test, labelNames, traintime)

    for model, name in modelsList:
        utilities.printModelSummary(model)
        

# usage: python ml/covmat.py datasets/filename.csv
if __name__ == "__main__":
    filename = sys.argv[1]
    targetCol = sys.argv[2:]
    main(filename, targetCol)
