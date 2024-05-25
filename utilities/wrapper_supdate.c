#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    // Check if the correct number of arguments are provided
    if (argc != 3) {
        printf("Usage: %s <resource_path> <correct_context>\n", argv[0]);
        return 1;
    }

    // Build the command string
    char command[256];  // Adjust size as needed
    snprintf(command, sizeof(command), "sudo scontrol update partitionname=%s allowgroups=%s", argv[1], argv[2]);

    // Execute the command
    int result = system(command);

    // Check if the command executed successfully
    return result;
}
