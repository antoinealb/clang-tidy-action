import unittest
import analyze

class CleanupCompileCommandsTestCase(unittest.TestCase):
    def test_simple_case(self):
        initial = [{
            "arguments": [
                "arm-none-eabi-gcc",
                "-c",
                "-mcpu=cortex-m4",
                "-Os",
                "-ggdb",
                "-fomit-frame-pointer",
                "-falign-functions=16",
                "-fno-common",
                "-ffunction-sections",
                "-fdata-sections",
                "-fno-common",
                "-Wall",
                "-Wextra",
                "-Wundef",
                "-Wstrict-prototypes",
                "-Wa,-alms=build/lst/hal.lst",
                "-DUAVCAN_TOSTRING=0",
                "-DUAVCAN_STM32_NUM_IFACES=1",
                "-DCVRA_NO_DYNAMIC_ALLOCATION=1",
                "-DTHUMB_PRESENT",
                "-mno-thumb-interwork",
                "-DTHUMB_NO_INTERWORKING",
                "-mthumb",
                "-DTHUMB",
                "-I.",
                "-I../lib/ChibiOS/os/common/portability/GCC",
                "-I../lib/ChibiOS/os/common/startup/ARMCMx/compilers/GCC",
                "-I../lib/ChibiOS/os/common/startup/ARMCMx/devices/STM32F3xx",
                "-Idsdlc_generated",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/hal.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/hal.c"
        }]
        want = [{
            "arguments": [
                "arm-none-eabi-gcc",
                "-c",
                "-Wall",
                "-Wextra",
                "-Wundef",
                "-Wstrict-prototypes",
                "-Wa,-alms=build/lst/hal.lst",
                "-DUAVCAN_TOSTRING=0",
                "-DUAVCAN_STM32_NUM_IFACES=1",
                "-DCVRA_NO_DYNAMIC_ALLOCATION=1",
                "-DTHUMB_PRESENT",
                "-DTHUMB_NO_INTERWORKING",
                "-DTHUMB",
                "-I.",
                "-I../lib/ChibiOS/os/common/portability/GCC",
                "-I../lib/ChibiOS/os/common/startup/ARMCMx/compilers/GCC",
                "-I../lib/ChibiOS/os/common/startup/ARMCMx/devices/STM32F3xx",
                "-Idsdlc_generated",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/hal.c",
                # TODO(antoinealb): This is only required on my laptop because I did not install clang correctly
                "-I~/.local/arm/arm-none-eabi/include/"

            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/hal.c"
        }]

        got = analyze.cleanup_compile_db(initial)
        self.maxDiff = None
        self.assertDictEqual(got[0], want[0])

    def test_merge_compile_db(self):
        db1 = [{
            "arguments": [
                "arm-none-eabi-gcc",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/hal.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/hal.c"
        },
        {
            "arguments": [
                "arm-none-eabi-gcc",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/file2.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/file2.c"
        },
        ]

        # First file is identical, but comes from another directory.second file
        # is different
        db2 = [{
            "arguments": [
                "arm-none-eabi-gcc",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/hal.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware/tests",
            "file": "../../lib/ChibiOS/os/hal/src/hal.c"
        },
        {
            "arguments": [
                "arm-none-eabi-gcc",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/file3.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/file3.c"
        },
        ]

        want = [{
            "arguments": [
                "arm-none-eabi-gcc",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/hal.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/hal.c"
        },
        {
            "arguments": [
                "arm-none-eabi-gcc",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/file2.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/file2.c"
        },
        {
            "arguments": [
                "arm-none-eabi-gcc",
                "-o",
                "build/obj/hal.o",
                "../lib/ChibiOS/os/hal/src/file3.c"
            ],
            "directory": "/Users/antoinealb/src/cvra/robot-software/can-io-firmware",
            "file": "../lib/ChibiOS/os/hal/src/file3.c"
        },
        ]

        got = analyze.merge_compile_commands(db1, db2)

        self.maxDiff = None
        self.assertEqual(want, got)

