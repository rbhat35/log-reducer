#!/usr/bin/python
def func1():
    file = open("../tests/test_case2.txt", "r+")


    file.write("Hello World \n")

    data = file.read()
    file.close()

def func2():
    file = open("../tests/test_case2.txt", "r+")
    data = file.read()
    file.close()

if __name__ == '__main__':

    func1()
   # func2()
