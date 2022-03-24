# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
"""Logistic Regression base functions

Provides base functionality of logistic regression based on 'Homomorphic training of 30,000 logistic regression models'
   (https://eprint.iacr.org/2019/425) by Bergamaschi et al.
"""

import numpy as np


# Sigmoid function
def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


# 3-degree polynomial representation of sigmoid function, effective in range of [-5, 5]
def sigmoid_poly3(x):
    return 0.5 - 1.20096 * (x / 8.0) + 0.81562 * (x / 8.0) ** 3


# 4-degree polynomial representation of log(sigmoid(x)) function, effective in range of [-5, 5]
def log_sig4(x):
    return 0.000527 * x ** 4 - 0.0822 * x ** 2 + 0.5 * x - 0.78


# Realign target to -1, 1 and calculate X@y'
def get_z(X, y, add1=True):
    if add1:
        X_ = np.concatenate([np.ones((X.shape[0], 1)), X], axis=1)
    else:
        X_ = np.array(X)
    y_ = 2 * y - 1
    z = X_ * y_[:, None]
    return np.array(z)


# Compute initial weight for logistic regression
def get_initweight(X, y, add1=True):
    n = X.shape[0]
    z = get_z(X, y, add1)
    return np.sum(z, axis=0) / n


# get evaluation metrics (accuracy, f1 score, etc.)
def get_eval_metrics(actual, predicted):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for a, p in zip(actual, predicted):
        if a == 1 and p == 1:
            tp += 1
        elif a == 1 and p == 0:
            fn += 1
        elif a == 0 and p == 1:
            fp += 1
        else:
            tn += 1

    acc = (tp + tn) / (tp + fp + tn + fn)
    if tp + fp > 0:
        precision = tp / (tp + fp)  # correct 1s over predicted 1s
    else:
        precision = 0.0

    if tp + fn > 0:
        recall = tp / (tp + fn)  # correct 1s over actual 1s
    else:
        recall = 0.0

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return acc, precision, recall, f1


# loss/gradient descent with standard sigmoid
def get_lgd(X, y, w):
    n = X.shape[0]
    z = get_z(X, y)
    zw = z @ w

    # calculate loss
    jw = np.sum(np.log(1 + np.exp(-zw))) / n

    # calculate gradient descent
    dw = 1.0 / (1 + np.exp(zw))
    dzw = z * dw[:, None]
    djw = -np.sum(dzw, axis=0) / n

    return jw, djw


# loss/gradient descent with poly3 sigmoid
def get_lgd_poly3(X, y, w):
    n = X.shape[0]
    z = get_z(X, y)
    zw = z @ w

    # calculate loss
    jw = np.sum(-log_sig4(zw)) / n

    # calculate gradient descent
    dw = sigmoid_poly3(zw)
    dzw = z * dw[:, None]
    djw = -np.sum(dzw, axis=0) / n

    return jw, djw


# test standard sigmoid
def test(X, y, w, add1=True):
    if add1:
        X_ = np.concatenate([np.ones((X.shape[0], 1)), X], axis=1)
    else:
        X_ = np.array(X)

    y_ = np.array([])
    for xi in X_:
        xiw = np.inner(xi, w)
        yi = sigmoid(xiw)  # 1./(1+np.exp(-xiw))
        if yi > 0.5:
            yi = 1
        else:
            yi = 0

        y_ = np.append(y_, yi)

    acc, _, recall, f1 = get_eval_metrics(y, y_)
    return np.array(y_), acc, recall, f1


# test poly3 sigmoid
def test_poly3(X, y, w, add1=True):
    if add1:
        X_ = np.concatenate([np.ones((X.shape[0], 1)), X], axis=1)
    else:
        X_ = np.array(X)

    y_ = np.array([])

    for xi in X_:
        xiw = np.inner(xi, w)
        yi = sigmoid_poly3(-xiw)  # 1./(1+np.exp(-xiw))
        if yi > 0.5:
            yi = 1
        else:
            yi = 0

        y_ = np.append(y_, yi)

    acc, _, recall, f1 = get_eval_metrics(y, y_)
    return np.array(y_), acc, recall, f1
