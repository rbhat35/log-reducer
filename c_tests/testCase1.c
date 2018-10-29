#include <stdio.h>



/*

Compile:
gcc testCase1.c -o testCase1.out

Run:
./testCase1.out

*/
void read();
void write();

int main() {
    read();
    write();
}

void read() {
    FILE *fp;

    fp = fopen("test.txt", "w+");
    //    fprintf(fp, "This is testing for fprintf...\n");
    fputs("This is testing for fputs...\n", fp);
    fclose(fp);
}

void write() {
    FILE *fp;

    char buff[255];
    fp = fopen("test.txt", "r");
    fgets(buff, 255, (FILE*)fp);
    printf("%s\n", buff );
}