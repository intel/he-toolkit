# CI Notes
There are known issues when compiling with clang. 

| Compiler Ver | Ubuntu-20 Status | Ubuntu-22 Status |
|--------------|------------------|-----------------:|
| Clang-10     | Pass             | N/A              |
| Clang-11     | Pass             | Pass             |
| Clang-12     | Fail*            | Fail*            |
| Clang-13     | N/A              | Fail*            |
| Clang-14     | N/A              | Pass             |

\* Fail to link OpenMP library or find OpenMP flags