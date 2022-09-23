# Configurable PSI Deployment

## Introduction
Private Set Intersection (PSI) allows two parties to compute the set
intersection of their respective sets of encrypted data without revealing any
information outside of the elements present in the intersecting set. This PSI
deployment is built on top of [HElib](https://github.com/homenc/HElib) and
given a client and server set computes an SQL-like query against the server
set.


## Requirements
```
HElib >= v2.2.1
HElib utils (for encrypt and decrypt)
```
The easiest method for installing the required dependencies of this deployment
is to use `hekit` to install the `recipes/config-psi.toml` recipe file.


## Usage
The `config_psi` directory is split into `psi` and `scripts`. The `psi`
directory contains code which performs the core PSI operation. The `scrips`
directory contains utility methods for encoding and decoding data.

Before using the encode/decode python scripts or running the included pytests
it is recommended to source the `setenv.sh` file to set some environment
variables required by the scripts and tests. One can source the file with
```bash
source setenv.sh
```

### Example data
All input data is in CSV form containing space separated data like the
following
```
column_one column_two column_three
data1 dataTwo 3
1stCol secondCol 4
```
The first row is the column headings, and the subsequent rows are the input
data. These columns can have alphanumeric, alphabetical, and numeric values.

### Encode
To encode data like the example shown above, users can use the script provided
in `scripts/encode.py`.

This script performs two types of encoding; client
encoding (default), and server encoding when supplied the `--server` flag.
Server encoding attempts to encode each row and column entry as a single
plaintext whereas the client encoding attempts to pack each query row into a
single row of plaintexts.

The encoder also accepts an optional `config` via `--config <config-file>`. If
none is provided then the encoder will use the default config file provided in
`scripts/config.toml`. This config file provides information on how to encode
the data and is where the user can specify the main HE parameters (`m` and `p`),
the number of columns, segmentations, value format of the data columns
{alphanumeric, alphabetical, numeric}, and any composite columns. To see an
example of this look at this example [config.toml](scripts/config.toml).

The encoder outputs the encoded data to stdout and thus saving the output to a
file one can use
```
./encode.py data.raw > data.encoded
```
to save the encoded data to a file called `data.encoded`. To see an example
output of the encoder see the
[example_result.ptxt](scripts/example_result.ptxt).

### Encrypt
To encrypt encoded data, use the provided HElib utilities in `HElib/utils`.
Usage documentation for this can be found
[here](https://github.com/homenc/HElib/tree/master/utils).

**NOTE:** The `create-context` utilities is required to produce the necessary
encryption/decryption keys.

### PSI
The PSI deployment performs the PSI computation between two
plaintext/ciphertext datasets using a custom query. The query can be passed via
what we call a `table file`. This table file has the following format
```
# Comments are allowed and ignored along with empty lines by the PSI program

# The following line is the TABLE description
TABLE (column_one (1), column_two, column_three (2))

# The following is the query
column_one AND (column_two OR column_three)
```
The `TABLE(...)` line describes the structure of the database table. It is a
list of the column headers followed by an optional dimension encased in
brackets. If no dimension is provided then the value defaults to 1.

**NOTE:** The current format for column headers must be underscore `_`
separated alphabetical characters only. If another character or number is
present in the column name this will produce an error.

The query line contains the SQL-like query that the user wants to perform. The
supported operators {AND, OR} must be uppercase and the column names must match
those present in the `TABLE(...)` string.

### Decrypt
To decrypt encoded data, use the provided HElib utilities in `HElib/utils`.
Usage documentation for this can be found
[here](https://github.com/homenc/HElib/tree/master/utils).

### Decode
To decode data, users can use the script provided in `scripts/decode.py`.

This script has a similar usage to the encoder script as it also accepts an
optional config file via `--config <config-file>`.

The decode script also accepts the flag `--entries ENTRIES` which signifies the
number of plaintext entries required to decode from the input file.

**NOTE:** This cannot exceed the total number of plaintext entries present in
the file.

The decoder will parse the input file and output which rows of the returned a
match against the specified query.

## Troubleshooting
