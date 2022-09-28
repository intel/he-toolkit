
## Introduction

This directory contains helper scripts for encoding and decoding data related
to the configurable PSI deployment.

## Encode
The `encode.py` script is used for encoding raw data. To view the usage
description, run the script with the help option
```bash
./encode.py -h
```

The encoder expects raw data in CSV format as input. This data will be rows of
space separated entries where the first row contains column headings and the
subsequent rows contain the raw data entries. These entries can be
alphanumeric, alphabetical, or numeric.

The encoder can be used to encode both query (client) and database (server)
data. By default the encoder will perform client encoding but using the
`--server` flag, the encoder will perform server encoding instead. 

Server encoding attempts to encode each row and column entry as a single
plaintext whereas the client encoding attempts to pack each raw query row into
a single row of plaintexts.

The encoder additionally accepts an optional config file via `--config
<config-file>`. If none is provided then the encoder will use the default
config file provided in [config.toml](config.toml) which can be used as an
example.

This config file specifies information on how to encode the data through the
specification of the main HE parameters (`m` and `p`) as well as descriptors
about the column and data entry formats.

By default the encoder outputs to stdout, thus to save the output to a file one
can use
```bash
./encode.py data.raw > data.encoded
```
This will encode the data in `data.raw` into plaintext(s) written to
`data.encoded`. To see an example plaintext output of the encoder see
[example_result.ptxt](example_result.ptxt).

## Decode
The `decode.py` script is used for decoding plaintext results from the
configurable PSI program. To view the usage description, run the script with
the help option
```bash
./decode.py -h
```

The decoder script reads in plaintext data which is expected to only contain
the values {0,1} in its valid form. Like the encoder, this script also accepts
an optional config file via `--config <config-file>`.

Additionally, one can specify the number of plaintext entries for the decoder
to read from the file with `--entries ENTRIES`. **NOTE:** This number cannot
exceed the total number of plaintext entries contained in the input file.

Given a plaintext entry like below
```
1
{"HElibVersion":"2.2.0","content":{"scheme":"BGV","slots":[[1],[0],[1],[0]]},"serializationVersion":"0.0.1","type":"Ptxt"}
```
the decoder will read the values of the `slots` entry of the JSON object and
will return a positive result every time it detects a 1.

For example, given the plaintext provided above the decoder will produce
```
Match on line '1'
Match on line '3'
```

The decoder will notify the user of any entries it views as corrupted if it
detects any value greater than 1.
