# HE Tools

## HE Algebras

The program `healg.py` given the plaintext prime `p` and the required number of
p-boxes `d` returns the available algebras.

### Dependencies
- python >= 3.8
- factor (common unix utility)

### Setup

Before use of the `healg` tool we must generate a list of primes that the tool
uses.  This can be achieved by running the supplied script `gen_primes.sh`
without any arguments. A resultant `primes.txt` file is created.

### Running

To run the tool, simply provide a single prime or a range where primes may be,
or a combination of the two.  For example, if we wish to search for algebras
where the prime is 2 and those between 11 and 25 inclusive, and 31 then we can
run the following,

```bash
./healg.py -p 2,11-25,31
```

By default, `p` is 2 and `d`is 1 if not provided. Searching for algebras that
give `d` larger than 1 simply pass the flag and argument in a similar manner to `p`.

```bash
./healg.py -p 2,11-25,31 -d 2,4-5
```
Here, we are searching algebras with the same `p`, but with `d` values of 2 and
between 4 to 5, inclusive.

The table retuned by the searches have the following column headers shown below
with their meanings,

| Header | Meaning |
| --- | --- |
| `p` | plaintext prime |
| `d` | number of coefficients in a slot (a.k.a. p-boxes) |
| `m` | order of the cyclotomic polynomial |
| `phi(m)` | the Euler totient of m which is the degree of the ciphertext and plaintext polynomial |
| `nslots` | the number of slots in a ciphertext and plaintext polynomial (`phi(m)` / `d`) |


For more information run `./healg.py -h`


### Known issues

The tool is dependent on the `factor` utility. There is a hard limit at
representing numbers if `factor` has not been compiled with the GMP library.

The primes that can be used are only those provided in the `primes.txt` file.
