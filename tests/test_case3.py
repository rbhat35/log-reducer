# Forward Trackability Test Case for High Fidelity Paper
# The two events, e1 and e2, produced by the two calls to funcU()
#   cannot be merged, since foward trackability is not preserved
#   with respect to funcZ()

def funcU():
    file = open("test_case3.txt", "r+")
    file.write("Hello Jane \n")
    file.close()


def funcZ():
    file = open("test_case3.txt", "r+")
    data = file.read()
    file.close()

if __name__ == '__main__':
    funcU()
    funcZ()
    funcU()
