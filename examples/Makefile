
CC=gcc
C_FLAGS= -O0

all: 1024.txt 256.txt readloop echo

readloop: readloop.c
	$(CC) $(C_FLAGS) $^ -o $@

1024.txt:
	python -c "print 'A'*1024" > 1024.txt

256.txt:
	python -c "print 'A'*256" > 256.txt


echo: echo.c
	$(CC) $(C_FLAGS) $^ -o $@

clean:
	rm readloop 1024.txt 256.txt
