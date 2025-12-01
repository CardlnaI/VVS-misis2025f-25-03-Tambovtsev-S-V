while True:
    print("Выбери уровень:")
    k = int(input())
    if k == 1:
        print("Выбирай:")
        print("1 -> upper")
        print("2 -> lower")
        print("3 -> capitalize")
        n = input()

        print('Введи строку:')
        l = str(input())

        if n == "1":
            print(l.upper())
        elif n == "2":
            print(l.lower())
        elif n == "3":
            print(l.capitalize())
        else:
            print("А все, адьос")

    elif k == 2:
        print("Выбирай:")
        print("1 -> count")
        print("2 -> find")
        print("3 -> index")
        print("4 -> replace")
        n = input()

        print('Введи строку:')
        l = str(input())
        print('Второй аргумент:')
        ll = str(input())
        if n == "1":
            print(l.count(ll))
        elif n == "2":
            print(l.find(ll))
        elif n == "3":
            print(l.index(ll))
        elif n == "4":
            print("Третий аргумент:")
            lll = str(input())
            print(l.replace(ll, lll))
        else:
            print("А все, адьос")

    elif k == 3:
        print("Выбирай:")
        print("1 -> split")
        print("2 -> join")
        n = input()

        print('Введи строку/массив через запятую:')
        l = str(input())
        print('Второй аргумент:')
        ll = str(input())
        if n == "1":
            print(l.split(ll))
        elif n == "2":
            print(ll.join(l.split(',')))
        else:
            print("А все, адьос")

    elif k == 4:
        print("Выбирай:")
        print("1 -> isdigit")
        print("2 -> isalpha")
        print("3 -> strip")
        print("4 -> format")
        n = input()

        print('Введи строку:')
        l = str(input())
        if n == "1":
            print(l.isdigit)
        elif n == "2":
            print(l.isalpha())
        elif n == "3":
            print('Второй аргумент:')
            ll = str(input())
            print(l.strip(ll))
        elif n == "4":
            print(format(l))
        else:
            print("А все, адьос")

    elif k == 5:
        print('Введи строку:')
        l = str(input())
        l = l.replace(';', ' ')
        l = l.replace(':', ' ')
        l = l.replace('-', ' ')
        l = (l.strip()).capitalize()
        print(l)
