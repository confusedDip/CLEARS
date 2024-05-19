#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

#define MAX_LINE_LENGTH 1024

int main(int argc, char *argv[]) {

    // Check if correct number of arguments are provided
    if (argc < 2) {
        fprintf(stderr, "Usage: %s group_name\n", argv[0]);
        return 1;
    }

    // Execute the groupadd command with sudo privileges
    if (setuid(0) != 0) {
        perror("setuid");
        return 1;
    }

    // Open a pipe to read the output of the "getent group" command
    FILE *pipe = popen("getent group", "r");
    if (pipe == NULL) {
        perror("Error opening pipe");
        return EXIT_FAILURE;
    }

    // Variables to store the highest assigned GID
    gid_t max_gid = 0;
    char line[MAX_LINE_LENGTH];

    // Read each line from the output of "getent group"
    while (fgets(line, MAX_LINE_LENGTH, pipe) != NULL) {
        // Tokenize the line using ":" as delimiter
        char *token = strtok(line, ":");
        int token_num = 0;
        gid_t gid = 0;
        // Parse the GID from the third token
        while (token != NULL) {
            token_num++;
            if (token_num == 3) {
                gid = atoi(token);
                break;
            }
            token = strtok(NULL, ":");
        }
        // Update max_gid if the current GID is higher
        if (gid > max_gid && strcmp(token, "nogroup") != 0) {
            max_gid = gid;
        }
    }

    // Close the pipe
    pclose(pipe);

    // Calculate the new GID
    gid_t new_gid = max_gid + 1;

    // Open /var/lib/extrausers/group for appending
    FILE *group_file = fopen("/var/lib/extrausers/group", "a");
    if (group_file == NULL) {
        perror("Error opening group file");
        return EXIT_FAILURE;
    }

    // Append the new group entry to the file
    const char *group_name = argv[1];
    fprintf(group_file, "%s:x:%d:", group_name, gid);
//    for (int i = 0; i < num_users; ++i) {
//        fprintf(group_file, "%s", users[i]);
//        if (i < num_users - 1) {
//            fprintf(group_file, ",");
//        }
//    }
    fprintf(group_file, "\n");

    // Close the file
    fclose(group_file);



    return EXIT_SUCCESS;
}
