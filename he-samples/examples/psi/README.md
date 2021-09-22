# Quick start
Generally, write a text file for the client set. For this example let's call it `client.txt`. Write some fruits. One fruit per line.
Make sure they are lower case and no whitespace either side.
Then run,
```bash
./psi client.txt -n 64
```
Although optional, it is a good idea to run the example with multiple threads
using the `-n` flag and specifying the number of threads.
There are three sets to choose from of differing sizes under `datasets`.
The default is `fruits.set`. To change the default set,
```bash
./psi client.txt --server dataset/us_states.set
```

For more options see
```bash
./psi -h
```
for help.


# How it works
Words are read in from client and server sets and hashed. The hash value, an
integer binary representation is encoded as a polynomial with the coefficients
in binary {0,1}. The plaintext prime in this example is always 2. The maximum
size of these polynomials are the order of p in Z_{m}^{\*}/<p> quotient group.
The default order of the cyclotomic polynomial used in the BGV scheme is 771
which gives a ord(p) = 16. You can change the default m by running you set
intersection
```bash
./psi client.txt --m 21845 --bits 100
```
Although this usually means increasing the number of bits for HElib to handle
noise at larger m values.

The client keeps a translation table for the client set of which hashes goes
with which word.  So that returned hashes can be translated back to words.

The maximum number of entries that the client set supports is the number of
slots in the plaintext/ciphertext.
