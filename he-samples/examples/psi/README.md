## How it works
PSI example uses [HElib library](https://github.com/homenc/HElib) to compute intersection of two given sets that were encrypted with BGV scheme, so it will return all the elements that are common to both sets.

The program reads words from client and server sets and computes a hash value for each word. The hash value, an integer binary representation is encoded as a polynomial with the coefficients in binary {0,1}. 

The encoded set for the client is encrypted, then intersection is computed and finally, the result is decrypted. The program keeps a translation table for the client set of which hashes goes with which word, so that returned hashes can be translated back to words.

The plaintext prime in this example is always 2 and the maximum size of these polynomials are the order of p in Z_{m}^{\*}/\<p\> quotient group.

The maximum number of entries that the client set supports is the number of slots in the plaintext/ciphertext.
  
## Usage
Create a text file and fill it with data for the client set. For example, create a file called `client.txt` and write some fruits. Add one item per line and make sure they are lower case and no whitespace either side.

Then, to run the example program execute
```bash
./psi client.txt 
```

## Flags
`<client-set>`: Client set.

`-n`: Number of threads. Default is `1`.

`--m`: Order of the cyclotomic polynomial. Default is `771`.

`--server`: Server set. Default is `./datasets/fruits.set`.

`--bits`: Number of big Q bits. Default is `100`.

`--ptxt`: Keep Client set in encoded plaintext. Default is `false`.

### Examples

Although optional, it is a good idea to run the example with multiple threads using the `-n` flag and specifying the number of threads.
```bash
./psi client.txt -n 64
```

There are three sets to choose from of differing sizes under [datasets](https://github.com/intel/he-toolkit/tree/new-example/he-samples/examples/psi/datasets) folder. The default is `fruits.set`, but it can be changed executing:
```bash
./psi client.txt --server datasets/us_states.set
```
  
The default order of the cyclotomic polynomial used in the BGV scheme is 771 which gives a ord(p) = 16. You can change the default m by running:
```bash
./psi client.txt --m 21845 --bits 100
```
Although this usually means increasing the number of bits for HElib to handle noise at larger m values.

For more options see
```bash
./psi -h
```
