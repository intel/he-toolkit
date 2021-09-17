# Sample Kernels
This directory contains sample kernels implemented using google test for Microsoft SEAL and PALISADE. These sample kernels are for operations which are more advanced than the micro-benchmarks but are not full standalone use cases. An example of such an operation is matrix multiplication for which we provide several different sample kernels showing alternative methods of implementing the same algorithm using different approaches, libraries, and schemes. The full set of available sample kernels for each library and a brief description are described in the details section. 

# Useage
This directory contains sample kernels which benchmark a set of more complex HE
operations in both SEAL and PALISADE.

To run the sample kernels such as dot product, call
```bash
# Note, these will take several minutes
$HE_SAMPLES/build/sample-kernels/sample-kernels-seal
$HE_SAMPLES/build/sample-kernels/sample-kernels-palisade
```
this will output timing results using google benchmark.

# Details
The following tables list and give a brief description of the different sample kernels available. All sample kernels use N = 8192 with 3 Coefficient modulus primes.

## Microsoft SEAL Sample Kernels

| **Sample Kernel Name**      | **Brief Description**|
| ----------------------------|---------------------- |
| **DotPlainBatchAxis\_CKKS** | Ciphertext-plaintext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ CKKS.       |
| **DotCipherBatchAxis\_CKKS**| Ciphertext-ciphertext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ CKKS.      |
| **MatMulVal\_CKKS**         | Matrix multiplication w/ matrix represented one row per ciphertext and manual computation using a collection of adds, multiplications, and rotations w/ CKKS.|
| **LogisticRegression\_CKKS**| Computes logistic regression inference using a batch of inputs.                                                                                              |
| **DotPlainBatchAxis\_BFV**  | Ciphertext-plaintext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ BFV.        |
| **DotCipherBatchAxis\_BFV** | Ciphertext-ciphertext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ BFV.       |
| **MatMulVal\_BFV**          | Matrix multiplication w/ matrix represented one row per ciphertext and manual computation using a collection of adds, multiplications, and rotations w/ BFV. |
| **MatMulRow\_BFV**          | Matrix multiplication w/ one matrix represented fully in a single ciphertext and the other matrix represented two rows at a time w/ BFV.                     |


## PALISADE Sample Kernels

|**Sample Kernel Name**      |**Brief Description**                                                                                                                                        |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**DotPlainBatchAxis\_CKKS** |Ciphertext-plaintext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ CKKS.       |
|**DotCipherBatchAxis\_CKKS**|Ciphertext-ciphertext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ CKKS.      |
|**MatMulEIP\_CKKS**         |Matrix multiplication w/ matrix represented one row per ciphertext using Palisade’s internal dot product calculation w/ CKKS.                                |
|**MatMulVal\_CKKS**         |Matrix multiplication w/ matrix represented one row per ciphertext and manual computation using a collection of adds, multiplications, and rotations w/ CKKS.|
|**MatMulRow\_CKKS**         |Matrix multiplication w/ one matrix represented fully in a single ciphertext and the other matrix represented row by row w/ CKKS.                            |
|**LogisticRegression\_CKKS**|Computes logistic regression inference using a batch of inputs.                                                                                              |
|**DotPlainBatchAxis\_BFV**  |Ciphertext-plaintext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ BFV.        |
|**DotCipherBatchAxis\_BFV** |Ciphertext-ciphertext matrix multiplication w/ matrix represented as one element per ciphertext using a collection of adds and multiplications w/ BFV.       |
|**MatMulEIP\_BFV**          |Matrix multiplication w/ matrix represented one row per ciphertext using Palisade’s internal dot product calculation w/ BFV.                                 |
|**MatMulVal\_BFV**          |Matrix multiplication w/ matrix represented one row per ciphertext and manual computation using a collection of adds, multiplications, and rotations w/ BFV. |
|**MatMulRow\_BFV**          |Matrix multiplication w/ one matrix represented fully in a single ciphertext and the other matrix represented row by row w/ BFV.                             |

