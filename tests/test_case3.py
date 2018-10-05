import os

# Forward Trackability Test Case for High Fidelity Paper
# The two events, e1 and e2, produced by the two calls to funcU()
#   cannot be merged, since foward trackability is not preserved
#   with respect to funcZ()

def funcU():
    file = os.open("../tests/test_case3.txt", os.O_RDWR)
    os.write(file, "Hello Jane \n")
    os.close(file)


def funcZ():
    file = os.open("../tests/test_case3.txt", os.O_RDWR)
    data = os.read(file, 1000)
    os.close(file)

if __name__ == '__main__':
    funcU()
    funcZ()
    funcU()
