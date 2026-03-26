/* REQUIREMENT: REQ-IEC-005, REQ-IEC-006 — Device firmware integrity verification */
/**
 * Firmware checksum utility — validates device firmware integrity.
 *
 * This small C module simulates a wearable device firmware component
 * that calculates checksums for data integrity verification.
 *
 * Used in the Sentrik demo to showcase C/C++ analysis (clang-tidy/cppcheck).
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Intentional C/C++ findings for sentrik analyze-cpp demo */

/* FINDING: Use of strcpy (buffer overflow risk — MISRA/CWE-120) */
char device_serial[32];

void set_device_serial(const char *serial) {
    strcpy(device_serial, serial);  /* Should use strncpy */
}

/* FINDING: Use of gets (always unsafe — CWE-242) */
void read_user_input(char *buffer) {
    /* gets is always unsafe — removed in C11 but still flagged */
    /* gets(buffer); */
    /* Simulated unsafe pattern: */
    scanf("%s", buffer);  /* No length limit — buffer overflow risk */
}

/* FINDING: Use of sprintf without bounds checking */
char firmware_info[64];

void format_firmware_info(const char *version, int build) {
    sprintf(firmware_info, "FW-%s-build%d", version, build);  /* Should use snprintf */
}

/* FINDING: Unchecked malloc return */
int *allocate_readings(int count) {
    int *readings = (int *)malloc(count * sizeof(int));
    /* Missing NULL check — could dereference NULL pointer */
    memset(readings, 0, count * sizeof(int));
    return readings;
}

/* CRC-16 checksum for data integrity */
unsigned short crc16(const unsigned char *data, int length) {
    unsigned short crc = 0xFFFF;
    int i, j;

    for (i = 0; i < length; i++) {
        crc ^= data[i];
        for (j = 0; j < 8; j++) {
            if (crc & 1)
                crc = (crc >> 1) ^ 0xA001;
            else
                crc = crc >> 1;
        }
    }
    return crc;
}

/* Validate firmware image checksum */
int validate_firmware(const unsigned char *image, int size,
                      unsigned short expected_crc) {
    unsigned short actual_crc = crc16(image, size);
    return actual_crc == expected_crc;
}

/* Simple test */
int main() {
    set_device_serial("VS-PULSE-OX-001");
    format_firmware_info("2.1.0", 42);

    printf("Device: %s\n", device_serial);
    printf("Firmware: %s\n", firmware_info);

    unsigned char test_data[] = "Hello, VitalSync!";
    unsigned short checksum = crc16(test_data, strlen((char *)test_data));
    printf("CRC-16: 0x%04X\n", checksum);

    int valid = validate_firmware(test_data, strlen((char *)test_data), checksum);
    printf("Validation: %s\n", valid ? "PASS" : "FAIL");

    int *readings = allocate_readings(10);
    if (readings) {
        readings[0] = 72;  /* heart rate */
        readings[1] = 98;  /* spo2 */
        printf("HR: %d, SpO2: %d\n", readings[0], readings[1]);
        free(readings);
    }

    return 0;
}
