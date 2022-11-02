
## OS-Compiler's HE-Toolkit test

# Ubuntu 20.04

| Ubuntu 20.04 | HELIB | SEAL |
|--------------|-------|------|
| Clang-10     | Pass  | Pass |

#  Ubuntu 22.04

| Ubuntu 22.04 | HELIB | SEAL |
|--------------|------ |------|
| Clang-12     | Pass  | *    |
| Clang-14     | Pass  | Pass |

## Known Combatability Issues

| Ubuntu 20.04 | HELIB             | SEAL  |
|-----------   |-------------------|-------|
| Clang-10     | Pass              | Pass  |
| Clang-11     | Pass              | Pass  |
| Clang-12     | Pass              | Fail* |
| Clang-13     | Not Pre-installed |       |
| Clang-14     | Not Pre-installed |       |


| Ubuntu 22.04 |    HELIB                | SEAL  |
|-----------   |-------------------------|-------|
| Clang-10     | Not supported on the OS         |
| Clang-11     | Pass                    | Pass  |
| Clang-12     | Pass                    | Fail* |
| Clang-13     | Pass                    | Fail* |
| Clang-14     | Pass                    | Pass  |

\* Under investigation


