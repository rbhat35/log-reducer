import os

# Merge test case for High Fidelity Paper
# Here, forward and backwards trackability are preserved with regards to e1 and e2
# Thus a merge should be performed

def funcZ2():
    file = os.open("test_case5_U.txt", os.O_RDWR)
    os.write(file, "Hello Jane \n")
    os.close(file)

def funcV():
    file = os.open("test_case5_U.txt", os.O_RDWR)
    data = os.read(file, 1000)
    os.close(file)

    file = os.open("test_case5_U.txt", os.O_RDWR)
    data = os.read(file, 1000)
    os.close(file)

    file = os.open("test_case5_Z1.txt", os.O_RDWR)
    os.write(file, "Hello Jane \n")
    os.close(file)


def main():
    funcZ2()
    funcV()

if __name__ == '__main__':
    main()
