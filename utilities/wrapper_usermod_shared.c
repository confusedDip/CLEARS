#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_LINE_LENGTH 1024


int main(int argc, char *argv[]) {
    // Check if correct number of arguments are provided
    if (argc != 3) {
        fprintf(stderr, "Usage: %s group_name user_name\n", argv[0]);
        return 1;
    }

    // Execute the usermod command with elevated privileges
    if (setuid(0) != 0) {
        perror("setuid");
        return 1;
    }

    // Open /var/lib/extrausers/group for reading and writing
    FILE *group_file = fopen("/var/lib/extrausers/group", "r+");
    if (group_file == NULL) {
        perror("Error opening group file");
        return EXIT_FAILURE;
    }

    // Read each line from the file
    char line[MAX_LINE_LENGTH];
    while (fgets(line, MAX_LINE_LENGTH, group_file) != NULL) {

        // Check if the line starts with the group name
        if (strncmp(line, argv[1], strlen(argv[1])) == 0) {

            // Find the last colon in the line
            char *last_colon = strrchr(line, ':');
            if (last_colon != NULL) {
                // Move the file pointer to the position after the last colon
                fseek(group_file, last_colon - line + 1, SEEK_SET);
                fprintf(group_file, "%s,", argv[2]);

                // Move the file pointer to the end of the line
                fseek(group_file, 0, SEEK_END);
                // Add a newline character
                fprintf(group_file, "\n");
                break; // No need to continue searching
            }
        }
    }

    // Close the file
    fclose(group_file);

    // Close the file
    fclose(group_file);

    return 0;
}
