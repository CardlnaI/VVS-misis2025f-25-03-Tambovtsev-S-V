from symtable import Class


def summ(a, b):
    print(a + b)
def vich(a, b):
    print(a - b)
def pere(a, b):
    print(a * b)
def dele(a, b):
    print(a / b)

def ultra(a, b, c):
    if c == "+":
        print(a + b)
    if c == "-":
        print(a - b)
    if c == "*":
        print(a * b)
    if c == "/":
        print(a / b)

class calc:
    def init(self):
        self.result = 0

    def summ(self, a, b):
        print(a + b)

    def vich(self, a, b):
        print(a - b)

    def pere(self, a, b):
        print(a * b)

    def dele(self, a, b):
        print(a / b)


while True:
    print("choose level (1-4):")
    n = input()
    if n == '1':
        try:
            print("write A, B and (+, -, *, /):")
            a = int(input())
            b = int(input())
            c = input()
            if c == "+":
                print(a + b)
            if c == "-":
                print(a - b)
            if c == "*":
                print(a * b)
            if c == "/":
                print(a / b)
        except: print("ERROW 1")
    if n == '2':
        try:
            print("write A, B and (+, -, *, /):")
            a = int(input())
            b = int(input())
            c = input()
            if c == "+":
                summ(a, b)
            if c == "-":
                vich(a, b)
            if c == "*":
                pere(a, b)
            if c == "/":
                dele(a, b)
        except:
            print("ERROW 2")
    if n == '3':
        try:
            print("write A, B and (+, -, *, /):")
            a = int(input())
            b = int(input())
            c = input()
            ultra(a, b, c)
        except:
            print("ERROW 3")
    if n == '4':
        try:
            print("write A, B and (+, -, *, /):")
            a = int(input())
            b = int(input())
            c = input()
            if c == "+":
                calc.summ(a, b)
            if c == "-":
                calc.vich(a, b)
            if c == "*":
                calc.pere(a, b)
            if c == "/":
                calc.dele(a, b)
        except:
            print("ERROW 4")
