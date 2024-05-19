#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define BUFFER_SIZE 4096

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s project_file network_json\n", argv[0]);
        return 1;
    }

    const char *project_file = argv[1];
    const char *network_json = argv[2];

    // Execute the usermod command with elevated privileges
    if (setuid(0) != 0) {
        perror("setuid");
        return 1;
    }

    FILE *file = fopen(project_file, "w");
    if (file == NULL) {
        fprintf(stderr, "Failed to create project '%s': %s\n", project_file, strerror(errno));
        return 1;
    }

    if (fwrite(network_json, sizeof(char), strlen(network_json), file) != strlen(network_json)) {
        fprintf(stderr, "Failed to write network data to project '%s': %s\n", project_file, strerror(errno));
        fclose(file);
        return 1;
    }

    fclose(file);
    printf("Project '%s' created/updated successfully.\n", project_file);
    return 0;
}
