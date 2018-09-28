# Merge test case for High Fidelity Paper
# Here, forward and backwards trackability are preserved with regards to e1 and e2
# Thus a merge should be performed

def funcZ2():
    file = open("test_case5_U.txt", "r+")
    file.write("Hello Jane \n")
    file.close()

def funcV():
    file = open("test_case5_U.txt", "r+")
    data = file.read()
    file.close()

    file = open("test_case5_U.txt", "r+")
    data = file.read()
    file.close()

    file = open("test_case5_Z1.txt", "r+")
    file.write("Hello Jane \n")
    file.close()


def main():
    funcZ2()
    funcV()

if __name__ == '__main__':
    main()
