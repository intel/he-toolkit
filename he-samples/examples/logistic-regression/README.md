# Logistic/Linear Regression with Homomorphic Encryption
The logistic regression example provides a fast and scalable implementation of
SEAL CKKS HE scheme based logistic regression.  It will be built whenever SEAL
is enabled as part of HE Toolkit build.

This example is also capable of running a linear regression instead of the logistic regression. Logistic regression can be achieved by "wrapping" a mulitiple linear regression model with a sigmoid function. The sigmoid function can be skipped by using the `--linear_regression` option, effectively running a linear regression.

## Requirements
```
python3 >= 3.5
virtualenv
```
Packages needed for generating the synthetic datasets are automatically
installed in a virtual environment within
`$HE_SAMPLES/build/examples/logistic-regression/datasets/`.

## Usage
To run the example program execute
```bash
cd $HE_SAMPLES/build/examples/logistic-regression
./lr_test
```

### Flags
`--data`: Dataset name. Default is `lrtest_mid`.

There are four different synthetic datasets available for testing, which are
automatically generated during build time.

| Name | Features | # Samples |
| --- | --- | --- |
| lrtest_small | 40 | 500 |
| lrtest_mid | 80 | 2000 |
| lrtest_large | 120 | 10000 |
| lrtest_xlarge | 200 | 50000 |

`--poly_modulus_degree`: Polynomial modulus degree. Determines the
encoding slot count (half of the parameter) and encryption security level.
Default is `8192`, and recommended size is `{4096, 8192, 16384}`, and
must be a power of 2, with full range of `[1024, 32768]`.

`--compare`: Compare the HE logistic regression inference result with non-HE
inference for validation purposes. Default is `false`.

`--data_plain`: Run with the data as plaintext.

`--model_plain`: Run with the model as plaintext.

`--linear_regression`: Calculate linear regression instead of logistic regression.

`--security_level`: Security level. One of `[0, 128, 192, 256]`.

`--coeff_modulus`: Coefficient modulus (list of primes). The bit-lengths of the primes to be generated.

`--batch_size`: Batch size. 0 = automatic (poly_modulus_degree / 2). Max = poly_modulus_degree / 2.

`--scale`: Scaling parameter defining precision.

## Data Preparation
There are two example data preparation ipython notebooks in
[datasets](datasets) folder.

## Acknowledgment
[Kaggle home credit default risk](https://www.kaggle.com/c/home-credit-default-risk)
