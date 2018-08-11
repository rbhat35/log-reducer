SRC_DIR = ./src
BIN_DIR = ./bin

CC=gcc
LIBS = -laudit
L_INCLUDE = -L/usr/lib/x86_64-linux-gnu
H_INCLUDE = -I/usr/include

all: trace

SRCFILES := $(wildcard ${SRC_DIR}/*.c)
OBJFILES := $(patsubst %.c, %.o, ${SRCFILES})

trace: $(OBJFILES)
	echo $< $(LIBS)
	$(CC) -o $(BIN_DIR)/trace $< $(L_INCLUDE) $(LIBS)


$(OBJFILES): $(SRC_DIR)/%.o : $(SRC_DIR)/%.c
	$(CC) $(H_INCLUDE) -c $< -o $@


