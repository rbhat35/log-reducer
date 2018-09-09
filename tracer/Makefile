SRC_DIR = ./src
BIN_DIR = ./bin
APP_DIR = ./apps
INC_DIR = ./include
CC=gcc -O0 -g
LIBS = -laudit
CFLAGS_DEBUG = -DCONFIG_DEBUG
L_INCLUDE = -L/usr/lib/x86_64-linux-gnu -L/usr/local/lib
H_INCLUDE = -I/usr/include -I/usr/local/include -I$(INC_DIR)

all: trace capture

SRCFILES := $(wildcard ${SRC_DIR}/*.c)
OBJFILES := $(patsubst %.c, %.o, ${SRCFILES})

trace: $(APP_DIR)/trace.c
	$(CC) $^ $(L_INCLUDE) $(LIBS) -o $(BIN_DIR)/trace 

capture: $(OBJFILES)
	echo $(OBJFILES)
	$(CC) $(CFLAGS_DEBUG) $(H_INCLUDE) -c $(APP_DIR)/capture.c -o $(APP_DIR)/capture.o $(L_INCLUDE) $(LIBS) 
	$(CC) $(CFLAGS_DEBUG) $(H_INCLUDE) $(APP_DIR)/capture.o $^ $(L_INCLUDE) $(LIBS) -o $(BIN_DIR)/capture


clean:
	rm $(SRC_DIR)/*.o $(APP_DIR)/*.o

$(OBJFILES): $(SRC_DIR)/%.o : $(SRC_DIR)/%.c
	$(CC) $(CFLAGS_DEBUG) $(H_INCLUDE) -c $< -o $@
