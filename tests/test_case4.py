# Backward Compatibility Test Case for High Fidelity
# The two events, e1 and e2, produced by the two calls to funcV()
#   cannot be merged, since backward trackability is not preserved
#   with respect to funcZ()

def funcZ():
    file = open("test_case4.txt", "r+")
    file.write("Hello Jane \n")
    file.close()

def funcV():
    file = open("test_case4.txt", "r+")
    data = file.read()
    file.close()


def main():
    funcV()
    funcZ()
    funcV()

if __name__ == '__main__':

    main()
