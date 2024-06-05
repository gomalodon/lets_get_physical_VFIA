export PICO_SDK_PATH="/mnt/c/Program Files/Raspberry Pi/Pico SDK v1.5.1/pico-sdk"

pushd build

cmake .. && make -j 16