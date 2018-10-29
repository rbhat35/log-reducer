// opens, reads, and write a file.
#include<stdlib.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>
#include<unistd.h>
#include<stdio.h>

int main(int argc, char **argv) {
    int fd;
    int rc = 0;
    int bytes_read = 0;
    char buffer[2056];

    fd = open(argv[1], O_RDWR);
    // Read 24 bytes at a time.
    do {
        bytes_read += rc;
        rc = read(fd, buffer + bytes_read, 24);
    } while (rc > 0);

    buffer[bytes_read + 1] = '\0';

    write(1, buffer, bytes_read);
}
