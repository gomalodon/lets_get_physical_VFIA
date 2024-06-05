#include "App.h"

#include <assert.h>
#include <fcntl.h>
#include <inttypes.h>
#include <pthread.h>
#include <pwd.h>
#include <sgx_urts.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#include "Enclave_u.h"
#include "sgx_urts.h"

#define MAX_PATH FILENAME_MAX
#define DEBUG_OUTPUT

/* Global EID shared by multiple threads */
sgx_enclave_id_t global_eid = 0;

typedef struct _sgx_errlist_t {
    sgx_status_t err;
    const char *msg;
    const char *sug; /* Suggestion */
} sgx_errlist_t;

/* Error code returned by sgx_create_enclave */
static sgx_errlist_t sgx_errlist[] = {
    {SGX_ERROR_UNEXPECTED, "Unexpected error occurred.", NULL},
    {SGX_ERROR_INVALID_PARAMETER, "Invalid parameter.", NULL},
    {SGX_ERROR_OUT_OF_MEMORY, "Out of memory.", NULL},
    {SGX_ERROR_ENCLAVE_LOST, "Power transition occurred.", "Please refer to the sample \"PowerTransition\" for details."},
    {SGX_ERROR_INVALID_ENCLAVE, "Invalid enclave image.", NULL},
    {SGX_ERROR_INVALID_ENCLAVE_ID, "Invalid enclave identification.", NULL},
    {SGX_ERROR_INVALID_SIGNATURE, "Invalid enclave signature.", NULL},
    {SGX_ERROR_OUT_OF_EPC, "Out of EPC memory.", NULL},
    {SGX_ERROR_NO_DEVICE, "Invalid SGX device.", "Please make sure SGX module is enabled in the BIOS, and install SGX driver afterwards."},
    {SGX_ERROR_MEMORY_MAP_CONFLICT, "Memory map conflicted.", NULL},
    {SGX_ERROR_INVALID_METADATA, "Invalid enclave metadata.", NULL},
    {SGX_ERROR_DEVICE_BUSY, "SGX device was busy.", NULL},
    {SGX_ERROR_INVALID_VERSION, "Enclave version was invalid.", NULL},
    {SGX_ERROR_INVALID_ATTRIBUTE, "Enclave was not authorized.", NULL},
    {SGX_ERROR_ENCLAVE_FILE_ACCESS, "Can't open enclave file.", NULL},
};

/* Check error conditions for loading enclave */
void print_error_message(sgx_status_t ret) {
    size_t idx = 0;
    size_t ttl = sizeof sgx_errlist / sizeof sgx_errlist[0];

    for (idx = 0; idx < ttl; idx++) {
        if (ret == sgx_errlist[idx].err) {
            if (NULL != sgx_errlist[idx].sug) printf("Info: %s\n", sgx_errlist[idx].sug);
            printf("Error: %s\n", sgx_errlist[idx].msg);
            break;
        }
    }

    if (idx == ttl) printf("Error code is 0x%X. Please refer to the \"Intel SGX SDK Developer Reference\" for more details.\n", ret);
}

/* Initialize the enclave:
 *   Step 1: try to retrieve the launch token saved by last transaction
 *   Step 2: call sgx_create_enclave to initialize an enclave instance
 *   Step 3: save the launch token if it is updated
 */
int initialize_enclave(void) {
    char token_path[MAX_PATH] = {'\0'};
    sgx_launch_token_t token = {0};
    sgx_status_t ret = SGX_ERROR_UNEXPECTED;
    int updated = 0;

    /* Step 1: try to retrieve the launch token saved by last transaction
     *         if there is no token, then create a new one.
     */
    /* try to get the token saved in $HOME */
    const char *home_dir = getpwuid(getuid())->pw_dir;

    if (home_dir != NULL && (strlen(home_dir) + strlen("/") + sizeof(TOKEN_FILENAME) + 1) <= MAX_PATH) {
        /* compose the token path */
        strncpy(token_path, home_dir, strlen(home_dir));
        strncat(token_path, "/", strlen("/"));
        strncat(token_path, TOKEN_FILENAME, sizeof(TOKEN_FILENAME) + 1);
    } else {
        /* if token path is too long or $HOME is NULL */
        strncpy(token_path, TOKEN_FILENAME, sizeof(TOKEN_FILENAME));
    }

    FILE *fp = fopen(token_path, "rb");
    if (fp == NULL && (fp = fopen(token_path, "wb")) == NULL) {
        printf("Warning: Failed to create/open the launch token file \"%s\".\n", token_path);
    }

    if (fp != NULL) {
        /* read the token from saved file */
        size_t read_num = fread(token, 1, sizeof(sgx_launch_token_t), fp);
        if (read_num != 0 && read_num != sizeof(sgx_launch_token_t)) {
            /* if token is invalid, clear the buffer */
            memset(&token, 0x0, sizeof(sgx_launch_token_t));
            printf("Warning: Invalid launch token read from \"%s\".\n", token_path);
        }
    }
    /* Step 2: call sgx_create_enclave to initialize an enclave instance */
    /* Debug Support: set 2nd parameter to 1 */
    ret = sgx_create_enclave(ENCLAVE_FILENAME, SGX_DEBUG_FLAG, &token, &updated, &global_eid, NULL);
    if (ret != SGX_SUCCESS) {
        print_error_message(ret);
        if (fp != NULL) fclose(fp);
        return -1;
    }

    /* Step 3: save the launch token if it is updated */
    if (updated == FALSE || fp == NULL) {
        /* if the token is not updated, or file handler is invalid, do not perform saving */
        if (fp != NULL) fclose(fp);
        return 0;
    }

    /* reopen the file with write capablity */
    fp = freopen(token_path, "wb", fp);
    if (fp == NULL) return 0;
    size_t write_num = fwrite(token, 1, sizeof(sgx_launch_token_t), fp);
    if (write_num != sizeof(sgx_launch_token_t)) printf("Warning: Failed to save launch token to \"%s\".\n", token_path);
    fclose(fp);
    return 0;
}

/* OCall functions */
void ocall_print_string(const char *str) {
    /* Proxy/Bridge will check the length and null-terminate
     * the input string to prevent buffer overflow.
     */
    printf("%s", str);
    return;
}

void print_time() {
    struct timespec ts;
    timespec_get(&ts, TIME_UTC);
    time_t seconds = ts.tv_sec;

    // printf("%s", ctime(&seconds));  // just for comparison

    struct tm *t = localtime(&seconds);

    printf("Time: %04d-%02d-%02d %02d:%02d:%02d.%09ld\n", t->tm_year + 1900, t->tm_mon + 1, t->tm_mday, t->tm_hour, t->tm_min, t->tm_sec, ts.tv_nsec);
    return;
}

#define RSA_LEN 256

const uint8_t result_exp[RSA_LEN] = {
    0x2d, 0x3e, 0x35, 0x4d, 0x6d, 0xb7, 0xf1, 0xd2, 0x32, 0xce, 0x81, 0x52, 0x19, 0x75, 0xc2, 0x7b, 0x4f, 0xc1, 0x3a, 0x2f, 0x97, 0xdb, 0x48, 0x04,
    0xb4, 0xae, 0x95, 0xd0, 0x87, 0x3e, 0xfb, 0x82, 0xf9, 0x92, 0xe3, 0x1b, 0x59, 0x11, 0x58, 0x43, 0x21, 0x41, 0x02, 0xd5, 0x69, 0x28, 0x8d, 0xb4,
    0x9a, 0xd2, 0xaa, 0x2b, 0x36, 0xc1, 0xb7, 0xa1, 0xb4, 0x28, 0x77, 0xf4, 0x4f, 0xfe, 0xdc, 0x4c, 0xdb, 0x2d, 0x9a, 0x83, 0x0e, 0xe1, 0x8a, 0xff,
    0xb3, 0xc2, 0xc9, 0x25, 0xfb, 0xdc, 0x3e, 0xf9, 0xaf, 0xf5, 0x26, 0x46, 0xc0, 0xb2, 0xe0, 0xd7, 0x84, 0x1f, 0x25, 0xb4, 0x8b, 0x2e, 0x1b, 0xc3,
    0x67, 0x52, 0xf5, 0xa8, 0xee, 0xf1, 0x68, 0x5c, 0x7d, 0xd8, 0xdc, 0x26, 0x0b, 0x31, 0x82, 0xca, 0xe2, 0x45, 0x4b, 0x50, 0x29, 0xe3, 0x50, 0x63,
    0x00, 0xe3, 0xe9, 0xac, 0x19, 0x7a, 0xeb, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

/* Application entry */
int SGX_CDECL main(int argc, char *argv[]) {
    (void)(argc);
    (void)(argv);

    if (argc != 3) {
        printf("Need 2 arguments: delay, iterations\n");
        return -1;
    }

    int delay = atoi(argv[1]);
    int iterations = atoi(argv[2]);
    bool infinite = (iterations == 0) ? true : false;

    printf("Waiting %d us\n", delay);
    usleep(delay);

    // printf("Creating enclave...\n");
    /* Initialize the enclave */
    if (initialize_enclave() < 0) {
        print_time();
        printf("Could not init enclave\n");
        return -1;
    }
    // printf_helloworld(global_eid);

    // printf("init RSA...\n");
    uint8_t res_var = 0;
    rsa_init_ecall(global_eid, &res_var);

    if (res_var != 1) {
        print_time();
        printf("Could not init RSA!\n");
        goto done;
    }
    // printf("Successfully made init rsa\n");
    // printf("Now computing inside SGX...\n");

    print_time();
    printf("Started %d decryptions\n", iterations);
    while (infinite || iterations > 0) {
        uint8_t buffer[RSA_LEN] = {0};
        rsa_dec_ecall(global_eid, &res_var, buffer);

        if (memcmp(buffer, result_exp, RSA_LEN) != 0) {
            print_time();
            printf("Faulted result\n");
            printf("Result = %x\n", res_var);
            for (int i = 0; i < RSA_LEN; i++) {
                printf("0x%02x, ", buffer[i]);
            }
            printf("\n");
            // } else {
            // printf("meh - all fine\n");
        }
        iterations -= 1;
    }
    rsa_clean_ecall(global_eid, &res_var);

done:
    sgx_destroy_enclave(global_eid);
    printf("Exiting...\n");
    return 0;
}
