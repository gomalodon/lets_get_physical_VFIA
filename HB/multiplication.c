/**
 * The following code is inspired by the Plundervolt multiplication PoC code.
*/

#include <stdint.h>
#include <stdio.h>
#include <time.h>

char* concat(const char *s1, const char *s2) {
    char *result = malloc(strlen(s1) + strlen(s2) + 1); // +1 for the null-terminator
    // in real code you would check for errors in malloc here
    strcpy(result, s1);
    strcat(result, s2);
    return result;
}

char* get_time() {
    struct timespec ts;
    timespec_get(&ts, TIME_UTC);
    time_t seconds = ts.tv_sec;
    struct tm *t = localtime(&seconds);
    char *str = (char *)malloc(50 * sizeof(char));
    sprintf(str, "[%04d-%02d-%02d %02d:%02d:%02d.%09ld]", t->tm_year + 1900, t->tm_mon + 1, t->tm_mday, t->tm_hour, t->tm_min, t->tm_sec, ts.tv_nsec);
    return str;                                                                                                             
}  

void tee(char *str) {
    printf(str);
    fflush(stdout);
    FILE *output_file = fopen("/home/hackboard/udp/broadcast-log", "ab");
    if (output_file == NULL) {
        printf("Error opening file for writing.\n");
        return -1;
    }
    fprintf(output_file, str);
    fflush(output_file);
    fclose(output_file);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Argument required: print_info (0/1)\n");
        return -1;
    }
    int print_info = atoi(argv[1]);

    srand(time(NULL));
    uint64_t operand1 = (uint64_t)rand();
    uint64_t operand2 = (uint64_t)rand();
    uint64_t correct_a;
    uint64_t correct_b;

    int faulty = 0;

    char *str = (char *)malloc(1000 * sizeof(char));
    tee(concat(get_time(), " Starting multiplications...\n"));
    sprintf(str, "%s Operands: %llu == %llu\n", get_time(), operand1, operand2);
    tee(str);

    time_t last_print_time = 0;
    int interval = 5;

    do {
        correct_a = operand1 * operand2;
        correct_b = operand1 * operand2;
        if (correct_a != correct_b) {
            faulty = 1;
            sprintf(str, "%s Fault found: %llu =/= %llu for %llu and %llu\n", get_time(), correct_a, correct_b, operand1, operand2);
            tee(str);
        }

        if (print_info) {
            time_t current_time = time(NULL);
            if (current_time - last_print_time >= interval) {
                sprintf(str, "%s Info: %llu =?= %llu for %llu and %llu\n", get_time(), correct_a, correct_b, operand1, operand2);
                tee(str);
                last_print_time = current_time;
            }
        }
    } while (faulty == 0);
    if (faulty == 0) {
        tee(concat(get_time(), " No fault found\n"));
    }
    return 0;
}