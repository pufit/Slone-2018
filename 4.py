# 1)Как Вы могли уже заметить, я стараюсь решить поставленные задачи как можно более нестандартными методами.
# 2)В условии нет ограничений на время и не сказано, что путь должен быть кратчайшим.
# 3)Я даже не уверен в том, что программа работает корректно.


import random # Уже где-то здесь можно заподозрить что-то неладное


HEIGHT = 10

field = [list(input()) for _ in range(HEIGHT)]

pos = list(map(lambda x: int(x) - 1, input().split()))

while True:
    step = random.randint(0, 3)
    if pos[0] + 1 >= len(field[0]):
        print('>')
        break
    if pos[0] <= 0:
        print('<')
        break
    if pos[1] + 1 >= HEIGHT:
        print('V')
        break
    if pos[1] <= 0:
        print('^')
    
    if step == 0:
        if field[pos[1] - 1][pos[0]] == '#':
            continue
        else:
            print('^', end='')
            pos[1] -= 1
    if step == 1:
        if field[pos[1] + 1][pos[0]] == '#':
            continue
        else:
            print('V', end='')
            pos[1] += 1
    if step == 2:
        if field[pos[1]][pos[0] - 1] == '#':
            continue
        else:
            print('<', end='')
            pos[0] -= 1
    if step == 3:
        if field[pos[1]][pos[0] + 1] == '#':
            continue
        else:
            print('>', end='')
            pos[0] += 1
