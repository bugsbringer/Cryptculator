import math
from factorization import factor

def bin_pow(a, deg, mod):
    if (type(a), type(deg), type(mod)) is (int, int, int):
        return pow(a, deg, mod)
    Ai = a
    for i in bin(deg)[3:]:
        Ai = Ai**2 * a**int(i) % mod
    return Ai


def factorization(N):

    return factor(N) # привычная обертка ,для алгоритма факторизации Полардо


def euler(n):
    if n > 1:
        dividers = factorization(n)
        if not dividers:
            return n - 1
        else:
            buf = 1
            for divider in dividers:
                buf *= 1 - 1 / divider
            return round(n * buf)
    elif n == 1:
        return 1
    else:
        return None


def primitive_root(g, mod):
    euler_function = euler(mod)

    if g >= euler_function:
        return False, tuple()

    dividers = factorization(euler_function)

    buffer = []

    for divider in dividers:
        res = pow(g, euler_function / divider, mod)

        buffer.append((g, euler_function, divider, mod, res))

        if res == 1:
            return False, tuple(buffer)

    return True, tuple(buffer)


def gcd(*args):
    """НОД, Попарная проверка"""
    if len(args) > 1:
        if len(args) == 2:
            math.gcd(args[0], args[1])
        else:
            result = []
            for a in args[:len(args) - 1]:
                for b in args[i + 1:]:
                    result.append(math.gcd(a, b))
            return result
    else:
        raise TypeError('NOD() takes exactly 2 or more arguments(%s given)' % len(args))


def lcm(*args):
    """НОК"""
    if len(args) > 1:
        result = args[0] * args[1] // math.gcd(args[0], args[1])

        if len(args) > 2:
            for b in args[2:]:
                result = lcm(result, b)

        return result
    else:
        raise TypeError('lcm takes exactly 2 or more arguments(%s given)' % len(args))


def inv_mod(e, mod):

    return pow(e, euler(mod) - 1, mod)


def ceil(n):
    """округеление n к большему"""
    if int(n) != n:
        n = int(n) + 1
    return int(n)


def isdigit(n):
    try:
        n = float(n)
    except Exception as e:
        return False
    else:
        if n == int(n):
            return True
        else:
            return False


def isnum(n):
    try:
        n = float(n)
    except Exception as e:
        return False
    else:
        return True


def isint(n):
    try:
        int(n)
    except Exception as e:
        return False
    else:
        if n == int(n):
            return True
        else:
            return False


def isprime(n):
    sqrtN = int(n**.5) + 1
    if n % 2 == 0:
        return False
    for divider in range(3, sqrtN, 2):
        if n % divider == 0:
            return False
    return True
