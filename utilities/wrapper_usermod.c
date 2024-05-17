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

    char *command = "/usr/sbin/usermod";
    char *args[] = {command, "-aG", argv[1], argv[2], NULL};

    // Execute the command with the provided arguments
    if (execvp(command, args) == -1) {
        perror("execvp");
        return 1;
    }

    return 0;
}
