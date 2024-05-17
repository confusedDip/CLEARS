#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

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

    char *command = "/usr/sbin/groupadd";

    // Execute the command with the provided arguments
    if (execvp(command, argv) == -1) {
        perror("execvp");
        return 1;
    }

    return 0;
}
