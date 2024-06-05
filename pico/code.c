#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "hardware/uart.h"
// #include "pico/cyw43_arch.h"
#include "pico/multicore.h"
#include "pico/stdlib.h"
#include "pico/time.h"

#define TIMEOUT_MS 10000
#define UART_BUFFERSIZE 64000

#define UART_ID uart0
#define BAUD_RATE 115200
#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define FREQ 1000000
#define VR_ADDR 0x5E
#define SDA_PIN 16
#define SCL_PIN 17
#define TRIGGER_PIN 15
#define STARTUP_PIN 14

i2c_inst_t* i2c = i2c0;
// volatile bool is_writing = false;
// uint8_t* continuous_voltage = NULL;

// void print_time() {
//     struct timespec ts;
//     timespec_get(&ts, TIME_UTC);
//     time_t seconds = ts.tv_sec;

//     // printf("%s", ctime(&seconds));  // just for comparison

//     struct tm* t = localtime(&seconds);

//     printf("Time: %04d-%02d-%02d %02d:%02d:%02d.%09ld\n", t->tm_year + 1900, t->tm_mon + 1, t->tm_mday, t->tm_hour, t->tm_min, t->tm_sec, ts.tv_nsec);
//     return;
// }

void trigger() {
    gpio_put(TRIGGER_PIN, 1);
    sleep_ms(2);
    gpio_put(TRIGGER_PIN, 0);
}

// Defaults: trig = false, continuous = NULL
void write_voltage(uint8_t* voltage, bool trig, uint8_t* ret_value, uint32_t* delay) {
    if (trig) {
        trigger();
    }
    uint8_t data[2] = {0x21, *voltage};
    uint8_t ret[2] = {0x21, *ret_value};
    int w1 = i2c_write_blocking(i2c, VR_ADDR, data, 2, false);
    sleep_us(*delay);
    int w2 = i2c_write_blocking(i2c, VR_ADDR, ret, 2, false);
    if (w1 == PICO_ERROR_GENERIC)
        printf("Failed to write first packet\n");
    else if (w2 == PICO_ERROR_GENERIC)
        printf("Failed to write second packet\n");
    else
        printf("Written %d & %d bytes\n", w1, w2);
}

void write_single_voltage(uint8_t* voltage, bool trig) {
    if (trig) {
        trigger();
    }
    uint8_t data[2] = {0x21, *voltage};
    int w1 = i2c_write_blocking(i2c, VR_ADDR, data, 2, false);
    if (w1 == PICO_ERROR_GENERIC)
        printf("Failed to write packet\n");
    else
        printf("Written %d bytes\n", w1);
}

void write_i2c_command(uint8_t* cmd, uint8_t* data, bool trig) {
    if (trig) {
        trigger();
    }
    uint8_t packet[2] = {*cmd, *data};
    int w1 = i2c_write_blocking(i2c, VR_ADDR, packet, 2, false);
    if (w1 == PICO_ERROR_GENERIC)
        printf("Failed to write packet\n");
    else
        printf("Written %d bytes\n", w1);
}

// void blink(int n) {
//     while (n > 0) {
//         cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
//         sleep_ms(1000);
//         cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
//         sleep_ms(1000);
//         n--;
//     }
// }

// void led(bool on) { cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, (int)on); }

// void set_global_voltage(uint8_t* voltage) { continuous_voltage = *voltage == '\x00' ? NULL : voltage; }

// Defaults: timeout = 2000
void on_off(uint32_t timeout) {
    // set_global_voltage(NULL);
    gpio_put(STARTUP_PIN, 0);
    sleep_ms(timeout);
    gpio_put(STARTUP_PIN, 1);
}

// Defaults: startup_time = 31000, delay1 = 11000, delay2 = 2000, timeout = 2000
void restart(uint32_t startup_time, uint32_t delay1, uint32_t delay2, uint32_t timeout) {
    // set_global_voltage(NULL);
    on_off(delay1);
    sleep_ms(timeout);
    on_off(delay2);
    sleep_ms(startup_time);
}

char* read_stdio(int prefix) {
    char* buffer = (char*)malloc(UART_BUFFERSIZE + 1);
    if (buffer == NULL) {
        return NULL;
    }
    int i = 0;
    char c;
    if (prefix != '\0') {
        buffer[i++] = prefix;
    }
    while ((c = getchar()) != '\n' && i < UART_BUFFERSIZE) {
        buffer[i++] = c;
    }
    if (c != '\n') {
        printf("Input is too long. Cutting off\n");
    }
    buffer[i] = '\0';
    return buffer;
}

volatile bool timed_out = false;

int64_t alarm_callback(alarm_id_t id, void* user_data) {
    printf("Timeout reached in uart\n");
    timed_out = true;
    return 0;
}

char* read_uart() {
    char* buffer = (char*)malloc(UART_BUFFERSIZE + 1);
    if (buffer == NULL) {
        return NULL;
    }
    int i = 0;
    char c;
    // printf("reading\n");
    while (i < UART_BUFFERSIZE) {
        while (!timed_out && !uart_is_readable(UART_ID)) {
        }
        if (timed_out || (c = uart_getc(UART_ID)) == '\n') {
            break;
        }
        buffer[i++] = c;
        // printf("i: %d\n", i);
        // printf("c: %c\n", c);
    }
    // printf("11\n");
    buffer[i] = '\0';
    // printf("%s\n", buffer);
    return buffer;
}

void doVoltage() {
    uint8_t voltage = getchar();
    bool trig = getchar();
    uint8_t ret_value = getchar();
    if (ret_value == '\0') {
        printf("Writing single voltage %#x (Trigger: %d)\n", voltage, trig);
        write_single_voltage(&voltage, trig);
    } else {
        uint32_t delay = (getchar() << 24) | (getchar() << 16) | (getchar() << 8) | getchar();
        // if (ret_value == '\x00') ret_value = NULL;
        printf("Writing voltage %#x (Trigger: %d, Return: %#x, Delay: %d us)\n", voltage, trig, ret_value, delay);
        // print_time();
        write_voltage(&voltage, trig, &ret_value, &delay);
    }
}

void doCommand() {
    char* buffer = read_stdio('\0');
    if (buffer == NULL) {
        printf("Memory allocation failed\n");
        return;
    }
    printf("Send command: %s\n", buffer);
    uart_puts(UART_ID, strcat(buffer, "\n"));
    free(buffer);
}

void print_output_nonblocking() {
    alarm_id_t id = add_alarm_in_ms(TIMEOUT_MS, alarm_callback, NULL, false);
    uint8_t code = 255;
    char* uart_buffer = NULL;
    // printf("c: %d\n", code);
    while (!timed_out && !uart_is_readable(UART_ID)) {
    }
    if (!timed_out) {
        code = uart_getc(UART_ID);
        // printf("c: %d\n", code);
        uart_buffer = read_uart();
    } else {
        timed_out = false;
        if (uart_buffer == NULL || strlen(uart_buffer) == 0) {
            uart_buffer = strdup("No data");
        }
    }
    printf("UART RETURN\\|\\%d\\|\\%s", code, uart_buffer);
    printf("\n"); // sometimes the null bytes cut off
    if (uart_buffer != NULL) free(uart_buffer);
    cancel_alarm(id);
}

void doStartGlitch() {
    absolute_time_t t1 = get_absolute_time();
    uint32_t delay_after_write = (getchar() << 24) | (getchar() << 16) | (getchar() << 8) | getchar();
    char* buffer = read_stdio('s');
    printf("Starting and glitching \"%s\" with delay: %d\n", buffer, delay_after_write);
    // print_time();
    uart_puts(UART_ID, strcat(buffer, "\n"));
    free(buffer);
    sleep_us(delay_after_write);
    getchar();  // delete v
    doVoltage();
    absolute_time_t t2 = get_absolute_time();
    printf("Time diff between start and voltage: %llu us\n", absolute_time_diff_us(t1, t2));
    uart_puts(UART_ID, "r");

    print_output_nonblocking();
}

// void print_help() {
//     puts("\nCommands:");
//     puts("v (0x76): write_voltage(voltage: hex, trigger: 0x00? false : true, return_value: hex, delay: us)");
//     // puts("b (0x62): blink(nb: int)");
//     // puts("l (0x6c): led(0x00? off : on)");
//     puts("t (0x74): trigger()");
//     puts("o (0x6f): on_off()");
//     puts("r (0x72): restart()");
//     puts("c (0x63): send command");
//     puts("s (0x73): start program");
//     // puts("g (0x67): set_global_voltage(voltage: hex)");
//     puts("h (0x68): view all commands");
// }

void doI2CCommand() {
    uint8_t cmd = getchar();
    uint8_t data = getchar();
    bool trig = getchar();
    printf("Writing i2c command %#x %#x (Trigger: %d)\n", cmd, data, trig);
    write_i2c_command(&cmd, &data, trig);
}

void handleSerial() {
    while (true) {
        char cmd = getchar();
        printf("Received: %c\n", cmd);
        switch (cmd) {
            case 'i': {
                doI2CCommand();
                break;
            }
            case 'c': {
                doCommand();
                break;
            }
            case 's': {
                doStartGlitch();
                break;
            }
            case 'v': {
                doVoltage();
                break;
            }
            // case 'b': {
            //     int nb = getchar();
            //     printf("Blinking %d times\n", nb);
            //     blink(nb);
            //     break;
            // }
            // case 'l': {
            //     bool on = getchar();
            //     printf("Led: %d\n", on);
            //     led(on);
            //     break;
            // }
            case 't': {
                printf("Trigger\n");
                trigger();
                break;
            }
            case 'o': {
                printf("Switching On/Off\n");
                on_off(2000);
                break;
            }
            case 'r': {
                printf("Restarting\n");
                restart(31000, 11000, 2000, 2000);
                break;
            }
            // case 'g': {
            //     uint8_t voltage = getchar();
            //     printf("Setting global voltage to %#x\n", voltage);
            //     set_global_voltage(&voltage);
            //     break;
            // }
            case '\n':
            case '\r':
                break;
            // case 'h': {
            //     print_help();
            //     break;
            // }
            default:
                printf("\nUnrecognised command: %c\n", cmd);
                // print_help();
                break;
        }
        printf("Done\n");
    }
}

int main() {
    stdio_init_all();
    // if (cyw43_arch_init()) {  // Needed for LED
    //     printf("Wi-Fi init failed");
    //     return -1;
    // }
    i2c_init(i2c, FREQ);

    gpio_init(SDA_PIN);
    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SDA_PIN);

    gpio_init(SCL_PIN);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SCL_PIN);

    gpio_init(STARTUP_PIN);
    gpio_set_dir(STARTUP_PIN, GPIO_OUT);
    gpio_put(STARTUP_PIN, 1);

    gpio_init(TRIGGER_PIN);
    gpio_set_dir(TRIGGER_PIN, GPIO_OUT);

    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    // multicore_launch_core1(continuous_voltage_thread);
    // uint32_t resp = multicore_fifo_pop_blocking();
    // if (resp != 0) {
    //     printf("core not started correctly\n");
    //     return -1;
    // }

    // led(1);
    handleSerial();
    // uint8_t voltage = 0x1a;
    // bool trig = true;
    // uint8_t ret_value = 0x1d;
    // uint32_t delay = 100;
    // while (1) {
    //     write_voltage(&voltage, trig, &ret_value, &delay);
    //     sleep_ms(10);
    // }
    return 0;
}
