# Clang-tidy Github action

Features:

* Analyze your pull requests with clang-tidy, saving human revierwers time.
* Reports finding directly to the Github interface for the files changed, but can also be used on complete codebase.
* Requires a configuration database, but can be configured to achieve this in many ways.
* Provides a way to generate "fake compilers" that can be used for easy generation of your `compile_commands.json`.

## Configuration

This actions is configured by two files:

1. `.clang-tidy`.
    This file in your project contains instructions for clang-tidy about which checks should be enabled.
    See the [clang-tidy docs](https://clang.llvm.org/extra/clang-tidy/) for example.
2. Another file in JSON which specifies basic compile steps used to generate the compilation database.

This second file can look somehow like the one below.
This file defines two different subprojects, each with their own build system and compilation databases.
They use [Bear](TODO) (included in the action) to examine a live build process and extract `compile_commands.json` from it.
In order to avoid installing a full toolchain, fake compilers are used.

```json
{
    "fake_compilers": [
        "arm-none-eabi-gcc",
        "arm-none-eabi-g++",
        "arm-none-eabi-ld",
        "arm-none-eabi-objcopy",
        "arm-none-eabi-objdump",
    ],
    "compilation_commands_sources": [
        {
            "command": "cd can-io-firmware && make clean && bear gmake -j4",
            "path": "can-io-firmware/compile_commands.json"
        },
        {
            "command": "cd uwb-beacon-firmware && make clean && bear gmake -j4",
            "path": "uwb-beacon-firmware/compile_commands.json"
        },
    ]
}
```
