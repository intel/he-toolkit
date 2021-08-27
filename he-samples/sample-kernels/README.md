# Sample Kernels
This directory contains sample kernels which benchmark a set of more complex HE
operations in both SEAL and PALISADE.

To run the sample kernels such as dot product, call
```bash
# Note, these will take several minutes
$HE_SAMPLES/build/sample-kernels/sample-kernels-seal
$HE_SAMPLES/build/sample-kernels/sample-kernels-palisade
```
this will output timing results using google benchmark.
