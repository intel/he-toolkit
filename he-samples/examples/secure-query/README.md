# Secure Query Example

The secure query example is designed to serve as a reference and proof of concept for how the concepts and features of HE can be used to implement a database lookup in which both the database and query are encrypted during the entire lookup.

## Description
The secure query example implements a simple secure database query using the SEAL BFV HE scheme.
It will be built whenever SEAL is enabled as part of the he-toolkit build.
The example consists of 2 component classes and a main file.
 - SQClient implements basic client functionality including initializing the encryption context, key generation, and encrypting and decrypting database queries.
 - SQServer stores the encrypted database and implements the encrypted database query algorithm.
 - Main.cpp Program which creates an instance of SQClient with either default or user specified encryption parameters, an instance of SQServer is then also initialized with the chosen parameters. Next the application reads in a set of key/value pairs from a user specified csv file and encrypts them using the HE context. The user is then prompted to enter a search key and the results of the search are then displayed.

## Usage

To run it execute
```bash
	cd $HE_SAMPLES/build/examples/secure-query
	./secure-query
```
### Example output

The following shows an example of a run of the sample using the default encryption and database file.
```bash
	Initialize SEAL BFV scheme with default parameters[Y(default)|N]:
	SEAL BFV context initialized with following parameters
	Polymodulus degree: 8192
	Plain modulus: 17
	Key length: 8
	Input file to use for database or press enter to use default[us_state_capitals.csv]:
	Number of database entries: 50
	Encrypting database entries into Ciphertexts
	Input key value to use for database query:Oregon
	Querying database for key: Oregon
	Decoded database entry: Salem

	Total query elapsed time(seconds): (Time in seconds for database query)
	Records searched per second: (number of records searched per second)
```

### Default options

The default options are set to allow the demo to work well with the current example dataset. It uses the following parameters
 - Polymodulus degree: 8192
 - Plain Modulus: 17
 - Key length: 8 characters
 - Input database: us_state_capitals.csv (Has 50 entries consisting of key:value (state name : Capital name) First letter capitalized.

### Custom options

The sample also supports specifying custom encryption parameters and input options. This can be useful to test more secure settings as well as to adjust key length to support different database files. The sample uses the default SEAL security level of 128-bits but all security related values should be verified before use in a real application.
The encryption parameters which can be specified are
- A power-of-two poly modulus degree specified as e.g. "10" for degree 1024=2^10
 - Plain modulus, this must be prime and > than 17
 - Database key length: The maximum key length in characters, should be long enough to fit the longest key specified in the dataset.

Additionally a custom database can be specified. The format of this database has the format (key , value).

## Implementation Details

For this example, database keys are assumed to be char strings. With the default options, they are encoded into 2 4-bit chunks. This is done so that each chunk can be represented by the plain modulus of 17. The secure query lookup algorithm is based on using Fermat's little theorem to generate a mask from the query and for each database entry's key. This results in mask values of 1 for matches and 0 for non matches. This mask is then multiplied against the database entry value which is accumulated for all entries and returned. For this sample it is required that all entries possess a unique key.

## References

[Microsoft SEAL](https://github.com/microsoft/SEAL)

[Fermat's Little Theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem)

[HELib country db lookup sample](https://github.com/homenc/HElib/tree/master/examples/BGV_country_db_lookup)

## Acknowledgements

This database lookup example is a derived port of the BGV Country Lookup example code that ships with [HElib](https://github.com/homenc/HElib) and can be found [here](https://github.com/homenc/HElib/tree/master/examples/BGV_country_db_lookup).
