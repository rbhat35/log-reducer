import os

# Backward Compatibility Test Case for High Fidelity
# The two events, e1 and e2, produced by the two calls to funcV()
#   cannot be merged, since backward trackability is not preserved
#   with respect to funcZ()

def funcZ():
    file = os.open("test_case4.txt", os.O_RDWR)
    os.write(file, "Hello Jane \n")
    os.close(file)

def funcV():
    file = os.open("test_case4.txt", os.O_RDWR)
    data = os.read(file, 1000)
    os.close(file)


def main():
    funcV()
    funcZ()
    funcV()

if __name__ == '__main__':

    main()
