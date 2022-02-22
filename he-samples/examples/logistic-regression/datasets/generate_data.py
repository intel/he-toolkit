# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
"""Generate_data

Provides base functionality of the following:
1. Generating synthetic data
2. Training logistic regression model based on Efficient logistic regression training by
   Bergamaschi et. al (https://eprint.iacr.org/2019/425)
3. Save trained model and generated data for LRHE example
"""
from enum import Enum
import csv
import numpy as np
import argparse
import sklearn.datasets
import lr_base as lrb
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


def doTrain(Xtrain, ytrain, Xtest, ytest, epochs=10, verbose=False):
    """Efficient logistic regression training

  Efficient logistic regression training by Bergamaschi et. al (https://eprint.iacr.org/2019/425)
  Provides a fast/efficient logistic regression training with cleartext data

  Args:
    Xtrain (numpy.array): Training data samples in numpy 2d array
    ytrain (numpy.array): Target of training set
    Xtest (numpy.array): Test data samples for validation in numpy 2d array
    ytest (numpy.array): Target of test set for validation
    epochs (int): Number of training epochs. Default = 10
    verbose (bool): Set to True for printing training progress. Default = False

  Returns:
    bias (float): bias of logistic regression trained model
    weights (numpy.array): weights of logistic regression trained model
  """

    w = v = lrb.get_initweight(Xtrain, ytrain)

    lmbda = 0
    if verbose:
        print("== Logistic Regression Training ==")
    for i in range(epochs):
        learning_rate = 10.0 / ((i + 1) + 1)
        new_lmbda = (1.0 + np.sqrt(1 + 4 * lmbda ** 2)) / 2.0
        smoothing = (1 - lmbda) / new_lmbda
        lmbda = new_lmbda

        loss, dw = lrb.get_lgd(Xtrain, ytrain, v)

        new_w = v - learning_rate * dw
        new_v = (1 - smoothing) * new_w + smoothing * w

        if verbose:
            if epochs < 10:
                if i % (int(epochs / 5)) == 0:
                    _, acc, _, _ = lrb.test(Xtest, ytest, v)
                    print("Epoch: %s, - loss: %s - acc: %s" % (i, loss, acc))
            else:
                if i % (int(epochs / 10)) == 0:
                    _, acc, _, _ = lrb.test(Xtest, ytest, v)
                    print("Epoch: %s, - loss: %s - acc: %s" % (i, loss, acc))

        v = new_v
        w = new_w

        bias = v[0]
        weights = v[1:]
    return bias, weights


# DataMode enumeration
class DataMode(Enum):
    train = 0
    test = 1
    eval = 2


# Save data to csv file (Default suffix = _eval)
def saveData(dataName, X, y, datamode: DataMode = DataMode.eval):
    """Save data samples to csv file

  Stores the data samples to be used for the LRHE example.

  Args:
    dataName (str): data name prefix
    X (numpy.array): data samples to be stored in 2d numpy array
    y (numpy.array): targets to be stored in a 1d numpy array
    datamode (DataMode): Determines the suffix [train, test, eval]. Default = DataMode.eval
  """
    nFeatures = X.shape[1]
    suffix = datamode.name
    features = ["feature_" + str(i) for i in range(nFeatures)] + ["target"]

    data = [features] + np.concatenate((X, np.transpose([y])), axis=1).tolist()
    # Save to csv
    with open(dataName + "_" + suffix + ".csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(data)


# Save model (combine [bias, weights...] to csv file with suffix _lrmodel
def saveModel(dataName, b, w):
    """Save logistic regression model to csv file

  Stores the model to be used for the LRHE example.

  Args:
    dataName (str): data name prefix
    b (float): bias of LR model
    w (numpy.array): weights of LR model
  """
    lr_model = np.concatenate(([b], w), axis=0).tolist()
    with open(dataName + "_lrmodel.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(lr_model)


def generateSynData(nSamples, nFeatures):
    """Generate synthetic dataset

  Generates synthetic datasets with the use of sklearn.datasets.make_classification.
  Splits the entire dataset into train, test and eval with the ratio of 2:1:1.

  Note that this will generate purposely well-fitted data samples for LR training

  Args:
    nSamples (int): number of data samples
    nFeatures (int): number of features

  Returns:
    Xtrain (numpy.array): train dataset. 1/4 of nSamples
    ytrain (numpy.array): train target
    Xtest (numpy.array): test dataset. 1/4 of nSamples
    ytest (numpy.array): test target
    Xeval (numpy.array): eval dataset. 1/4 of nSamples
    yeval (numpy.array): eval target
  """

    data = sklearn.datasets.make_classification(
        n_samples=nSamples,
        n_features=nFeatures,
        n_classes=2,
        n_clusters_per_class=2,
        n_informative=2,
        n_redundant=0,
        n_repeated=0,
    )
    x = data[0]
    y = data[1]
    scaler = MinMaxScaler(feature_range=(-1.0, 1.0))
    X_scaled = scaler.fit_transform(x)
    Xtrain, Xtest, ytrain, ytest = train_test_split(
        X_scaled, y, test_size=0.5, random_state=50, shuffle=True, stratify=y
    )
    Xtest, Xeval, ytest, yeval = train_test_split(
        Xtest, ytest, test_size=0.5, random_state=50, shuffle=True, stratify=ytest
    )

    return Xtrain, ytrain, Xtest, ytest, Xeval, yeval


if __name__ == "__main__":
    """Base script to generate samples for LRHE example

  This script generates a set of synthetic dataset with various sizes, train
  a logistic regression model with each data, then stores them in csv files.
  Generation and training happens during he-samples build time.

  This script can also be used to generate user-defined synthetic dataset.
  If --samples and --features flags are set via command line, it will instead
  generate a synthetic data set and train LR model accordingly.
  """
    parser = argparse.ArgumentParser(
        description="Synthetic data generation and LR model training"
    )
    parser.add_argument(
        "--samples", "-s", default=0, type=int, help="# of samples to generate."
    )
    parser.add_argument("--features", "-f", default=0, type=int, help="# of features")
    parser.add_argument("--name", "-n", default=None, help="Data prefix")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Set to see training progress"
    )

    args = parser.parse_args()

    # if no flags, proceed to preset generation
    if args.samples == 0 and args.features == 0 and args.name == None:
        print("=== Synthetic data generation for logistic regression HE example ===")
        l_dataname = ["lrtest_small", "lrtest_mid", "lrtest_large", "lrtest_xlarge"]
        l_features = [40, 80, 120, 200]
        l_samples = [500, 2000, 10000, 50000]

        for dataname, n_features, n_samples in zip(l_dataname, l_features, l_samples):
            print(" - Generating", dataname, "dataset")
            # generates 4x samples - ratio (train:test:eval = 2:1:1)
            X_train, y_train, X_test, y_test, X_eval, y_eval = generateSynData(
                n_samples * 4, n_features
            )
            print(" - Training LR model...")
            bias, weights = doTrain(
                X_train, y_train, X_test, y_test, verbose=args.verbose
            )
            print(" - Storing LR model and eval data")
            saveModel(dataname, bias, weights)
            saveData(dataname, X_eval, y_eval)
        print("=== Data generation complete ===")
    # if all arguments are set, make custom data
    elif args.samples > 0 and args.features > 0 and args.name != None:
        print("=== Synthetic data generation for logistic regression HE example ===")
        print(
            " - Generating custom dataset :",
            args.name,
            " n_samples:",
            args.samples,
            " n_features:",
            args.features,
        )
        X_train, y_train, X_test, y_test, X_eval, y_eval = generateSynData(
            args.samples * 4, args.features
        )
        print(" - Training LR model...")
        bias, weights = doTrain(X_train, y_train, X_test, y_test, verbose=args.verbose)
        print(" - Storing LR model and eval data")
        saveModel(args.name, bias, weights)
        saveData(args.name, X_eval, y_eval)
        print("=== Data generation complete ===")
    # if less than 3 flags are defined, raise error
    else:
        raise ValueError(
            "All arguments are mutually exclusive. Set none or all, otherwise will not work"
        )
