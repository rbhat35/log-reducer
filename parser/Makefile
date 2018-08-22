SRC_DIR = ./src
BIN_DIR = ./bin
APP_DIR = ./apps
INC_DIR = ./include
CC=gcc
LIBS = -laudit -lipt
L_INCLUDE = -L/usr/lib/x86_64-linux-gnu -L/usr/local/lib
H_INCLUDE = -I/usr/include -I$(INC_DIR)

all: trace capture hello-pt

SRCFILES := $(wildcard ${SRC_DIR}/*.c)
OBJFILES := $(patsubst %.c, %.o, ${SRCFILES})

trace: $(OBJFILES)
	$(CC) -o $(BIN_DIR)/trace $< $(L_INCLUDE) $(LIBS)


capture : $(OBJFILES) $(APP_DIR)/capture.c
	$(CC) $(H_INCLUDE) $(APP_DIR)/capture.c $(L_INCLUDE) $(LIBS) -o $(BIN_DIR)/capture

hello-pt: $(OBJFILES) $(APP_DIR)/hello-pt.c
	$(CC) $(H_INCLUDE) $(APP_DIR)/hello-pt.c $(L_INCLUDE) $(LIBS) -o $(BIN_DIR)/hello-pt


$(OBJFILES): $(SRC_DIR)/%.o : $(SRC_DIR)/%.c
	$(CC) $(H_INCLUDE) -c $< -o $@
