cmake_minimum_required(VERSION 3.12)

set(ENV(PICO_SDK_PATH) "/mnt/c/Program Files/Raspberry Pi/Pico SDK v1.5.1/pico-sdk")
set(PICO_BOARD pico_w)

# initialize the SDK based on PICO_SDK_PATH
# note: this must happen before project()
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(test C CXX)

# initialize the Raspberry Pi Pico SDK
pico_sdk_init()

# rest of your project
# add_executable(picow_blink picow_blink.c)

# target_link_libraries(picow_blink 
#         pico_stdlib 
#         pico_cyw43_arch_none
# )


# # create map/bin/hex file etc.
# pico_add_extra_outputs(picow_blink)
# pico_enable_stdio_usb(picow_blink 1)
# pico_enable_stdio_uart(picow_blink 0)

# if (TARGET tinyusb_device)
#     add_executable(hello_world
#             hello_world.c
#             )

#     # pull in common dependencies
#     target_link_libraries(hello_world pico_stdlib)

#     # enable usb output, disable uart output
#     pico_enable_stdio_usb(hello_world 1)
#     pico_enable_stdio_uart(hello_world 0)

#     # create map/bin/hex/uf2 file etc.
#     pico_add_extra_outputs(hello_world)

# elseif(PICO_ON_DEVICE)
#     message(WARNING "not building hello_world because TinyUSB submodule is not initialized in the SDK")
# endif()


# add_executable(i2c 
#     i2c.c
# )

# # Create map/bin/hex/uf2 files
# pico_add_extra_outputs(i2c)

# # Link to pico_stdlib (gpio, time, etc. functions)
# target_link_libraries(i2c 
#     pico_stdlib
#     hardware_i2c
# )

# # Enable usb output, disable uart output
# pico_enable_stdio_usb(i2c 1)
# pico_enable_stdio_uart(i2c 0)


add_executable(code
    code.c
    )

target_link_libraries(code 
    pico_stdlib 
    # pico_cyw43_arch_none
    hardware_i2c 
    hardware_gpio
    pico_multicore
    )
# pico_generate_pio_header(code ${CMAKE_CURRENT_LIST_DIR}/blink.pio)

pico_enable_stdio_usb(code 1)
pico_enable_stdio_uart(code 0)

pico_add_extra_outputs(code)

add_executable(flash_nuke
        nuke.c
        )

target_link_libraries(flash_nuke
        pico_stdlib
        hardware_flash
        )

# It doesn't make sense to run this program from flash. Always build a
# RAM-only binary.
pico_set_binary_type(flash_nuke no_flash)

pico_add_extra_outputs(flash_nuke)
