def func1():
    file = open("test_case1.txt", "r+")


    file.write("Hello World \n")

    file.close()

def func2():
    file = open("test_case1.txt", "r+")
    data = file.read()
    file.close()

if __name__ == '__main__':

    func1()
    func2()
