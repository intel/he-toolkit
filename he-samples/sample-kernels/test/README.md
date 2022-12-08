# Unit Tests
This directory contains unit tests for the sample kernels built using both SEAL
and PALISADE. These tests are used to verify the accuracy of the various
[sample kernels](../) included in this project.

Assuming the sample kernels were built via `hekit` using the provided recipe
`sample-kernels.toml` they can run by calling
```bash
$HOME/.hekit/components/sample-kernels/seal/build/test/unit-test
$HOME/.hekit/components/sample-kernels/palisade/build/test/unit-test
```
