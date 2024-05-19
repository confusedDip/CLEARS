#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

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

    // Open /var/lib/extrausers/group for appending
    FILE *group_file = fopen("/var/lib/extrausers/group", "a");
    if (group_file == NULL) {
        perror("Error opening group file");
        return EXIT_FAILURE;
    }

    // Append the new group entry to the file
    const char *username = argv[2];

    fprintf(group_file, "%s", username);
    fprintf(group_file, ",");

    // Close the file
    fclose(group_file);

    return 0;
}
