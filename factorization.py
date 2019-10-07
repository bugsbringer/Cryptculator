from random import randint
from math import gcd


def miller_rabin_test(a, n, s, d):
    """Один тест Миллера-Рабина.
    Является ли число 2 <= a <= n-2 свидетелем простоты для числа n (n-1 = d * 2**s)
    Если вдруг среди чисел a**(d*2**0), ..., a**(d*2**s) перед какой-то 1 идёт не -1,
    то число n — составное, а a — не является свидетелем простоты."""
    x = pow(a, d, n)  # x = a**(d*2**0)
    if x in (1, n - 1):
        return True
    for r in range(s - 1):
        x = (x * x) % n  # Из числа a**(d*2**r) вычисляем a**(d*2**(r+1))
        if x == 1:  # Ну всё, число составное
            return False
        elif x == n - 1:  # Нашлась -1. Число a — свидетель простоты для n
            return True
    return False  # Даже тест Ферма не пройден: a**(n-1) != 1


def miller_rabin(n):
    """Проверяет простоту числа n>3, выполняя log2(n) тестов Миллера-Рабина"""
    # Ищем разложение n-1 = n-1 = d * 2**s
    s, d = 0, n - 1
    while d % 2 == 0:
        s, d = s + 1, d // 2
    for _ in range(n.bit_length()):  # Повторяем тест log2(n) раз.
        a = randint(2, n - 2)  # берём случайное число
        if not miller_rabin_test(a, n, s, d):  # Если тест не пройден, то число составное
            return False
    return True  # С вероятностью 1/n**2 число простое


def pollards_rho_iter(n):
    """Поиск делителя у нечётного составного числа"""
    # Начинаем с функции F(x) = x**2 + 1 из точки x=2. Обычно это срабатывает
    x = y = 2
    a = 1
    while True:
        d = 1
        while d == 1:  # Если 1 < d < n, то мы нашли делитель d
            x = (x * x + a) % n  # x = F(F(..(F(x)..))
            y = (y * y + a) % n
            y = (y * y + a) % n  # y = F(F(F(F(..(F(F(x))..))))   (в два раз больше раз F)
            d = gcd(n, abs(x - y))
        if d < n:  # Если 1 < d < n, то мы нашли делитель d
            return d
        # Редко бывает так, что для функции x**2 + 1 при старте с 2 делитель не находится
        # В этом случае используем F(x) = x**2 + a, и стартуем с другого случайного числа
        x = y = randint(1, n - 1)
        a = randint(-100, 100) % n


def factor(n):
    """Факторизация числа при помощи ро-метода Полларда и тестов Миллера-Рабина"""
    # Избавляемся от всех двоек, троек и пятёрок
    ans = []
    for x in (2, 3, 5):
        while n % x == 0:
            ans.append(x)
            n //= x
    if n == 1:
        pass  # n = 2**a * 3**b * 5**c
    elif miller_rabin(n):  # Остаток простой
        ans.append(n)
    else:  # Ищем делители
        d = pollards_rho_iter(n)
        ans.extend(factor(d))
        ans.extend(factor(n // d))

    return tuple(sorted(ans))
