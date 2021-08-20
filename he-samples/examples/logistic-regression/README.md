# Logistic Regression with Homomorphic Encryption
The logistic regression example provides a fast and scalable implementation of
SEAL CKKS HE scheme based logistic regression.  It will be built whenever SEAL
is enabled as part of HE Toolkit build.

## Requirements
```
python3 >= 3.5
virtualenv or python3-venv
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


`-poly_modulus_degree`: Polynomial modulus degree, which determines the
encoding slot count (half of the parameter) and encryption security level.
Default is `8192`, and recommended size is `{4096, 8192, 16384}`, and
must be a power of 2, with full range of `[1024, 32768]`.

`--docompare`: Compare the HE logistic regression inference result with non-HE
inference for validation purposes. Default is `false`.

## Data Preparation
There are two example data preparation ipython notebooks in
[datasets](datasets) folder.

## Acknowledgment
[Kaggle home credit default risk](https://www.kaggle.com/c/home-credit-default-risk)
