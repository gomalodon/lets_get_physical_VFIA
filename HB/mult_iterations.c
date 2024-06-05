/**
 * The following code is inspired by the Plundervolt multiplication PoC code.
*/

#include <stdbool.h> 
#include <stdint.h>
#include <stdio.h>
#include <time.h>

char* get_time() {
    struct timespec ts;
    timespec_get(&ts, TIME_UTC);
    time_t seconds = ts.tv_sec;
    struct tm *t = localtime(&seconds);
    char *str = (char *)malloc(50 * sizeof(char));
    sprintf(str, "[%04d-%02d-%02d %02d:%02d:%02d.%09ld]", t->tm_year + 1900, t->tm_mon + 1, t->tm_mday, t->tm_hour, t->tm_min, t->tm_sec, ts.tv_nsec);
    return str;                                                                                                             
}  

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Arguments required: delay, iterations\n");
        return -1;
    }
    int delay = atoi(argv[1]);
    int iterations = atoi(argv[2]);
    bool infinite = (iterations == 0)? true : false;

    printf("Waiting %d us\n", delay);
    usleep(delay);

    srand(time(NULL));
    uint64_t operand1 = (uint64_t)rand();
    uint64_t operand2 = (uint64_t)rand();
    uint64_t correct_a;
    uint64_t correct_b;

    int faults = 0;

    printf("%s Starting %d multiplications...\n", get_time(), iterations);
    printf("%s Operands: %llu == %llu\n", get_time(), operand1, operand2);

    while (infinite || iterations > 0) {
        correct_a = operand1 * operand2;
        correct_b = operand1 * operand2;
        if (correct_a != correct_b) {
            faults += 1;
            printf("%s Faulted result: %llu =/= %llu for %llu and %llu\n", get_time(), correct_a, correct_b, operand1, operand2);
        }
        iterations -= 1;
    }
    printf("%s Finished loop: iterations left = %d, faults = %d\n", get_time(), iterations, faults);
    return 0;
}