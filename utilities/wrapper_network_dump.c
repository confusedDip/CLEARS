#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>

#define BUFFER_SIZE 4096

// Updated main
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s project_file\n", argv[0]);
        return 1;
    }

    const char *project_file = argv[1];

    if (setuid(0) != 0) {
        perror("setuid");
        return 1;
    }

    FILE *file = fopen(project_file, "w");
    if (file == NULL) {
        fprintf(stderr, "Failed to create project '%s': %s\n", project_file, strerror(errno));
        return 1;
    }

    char buffer[BUFFER_SIZE];
    size_t bytes_read;

    while ((bytes_read = fread(buffer, 1, sizeof(buffer), stdin)) > 0) {
        if (fwrite(buffer, 1, bytes_read, file) != bytes_read) {
            fprintf(stderr, "Failed to write to project '%s': %s\n", project_file, strerror(errno));
            fclose(file);
            return 1;
        }
    }

    fclose(file);
    printf("Project '%s' created/updated successfully.\n", project_file);
    return 0;
}
