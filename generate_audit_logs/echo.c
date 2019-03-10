#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>


int main() {
    char buffer[80];
    char yn;
    printf("%d\n", getpid());
    while(1) {
        scanf("%s%c", &buffer, &yn);
        printf("%s%c", buffer, yn);
    }
}
