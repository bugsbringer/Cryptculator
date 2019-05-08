def bin_pow(a,pow,mod):
    Ai = a
    for i in bin(pow)[3:]:
        Ai = Ai**2 * a**int(i) % mod
    return Ai

def factorization(N):
    n = N
    dividers = []
    degrees = []
    if n > 2 and n % 2 == 0:
        dividers.append(2)
        quantity = 0
        while n % 2 == 0:
            n = n // 2
            quantity += 1
        degrees.append(quantity)

    sqrtN = ceil(n**0.5)
    if n > 2:
        for divider in range(3,sqrtN,2):
            if n % divider == 0:
                dividers.append(divider)
                quantity = 0
                while n % divider == 0:
                    n = n // divider
                    quantity += 1
                degrees.append(quantity)

                if n <= 1: break

    if n != 1 and n != N:
        dividers.append(n)
        degrees.append(1)

    return dividers,degrees

def factorization_ferma(n,multitreading=False):
    def fun(n):
        x = ceil(n**.5)
        k = 0
        while True:
            s = x+k
            y = (s**2-n)**.5
            if isint(y): break
            k += 1
        a = s + y
        b = s - y
        if a == 1 or b == 1:
            if n != N:
                dividers.append(int(n))
        else:
            if multitreading:
                from threading import Thread
                t1 = Thread(target=fun, args=(int(a),))
                t1.start()
                t1.join()
            else:
                fun(int(a))
            fun(int(b))

    N = n
    dividers = []
    degrees = []
    while n % 2 == 0:
        dividers.append(2)
        n = n // 2

    fun(n)
    dividers.sort()
    i = 0
    while i < len(dividers):
        degrees.append(dividers.count(dividers[i]))
        for j in range(len(dividers)-1,i,-1):
            if dividers[j] == dividers[i]:
                dividers.pop(j)
        i += 1
    return dividers,degrees

def euler(n):
    if n > 1:
        dividers = factorization(n)[0]
        if not dividers:
            return n - 1
        else:
            buf = 1
            for divider in dividers:
                buf *= 1 - 1/divider
            return round(n * buf)
    elif n == 1: return 1
    else: return None

def primitive_root(g,mod):
    euler = euler(mod)
    if g >= euler:
        return False,tuple()
    dividers = factorization(euler)[0]
    buffer = []
    for divider in dividers:
        res = pow(g, euler//divider, mod)
        buffer.append((g,euler,divider,mod,res))
        if res == 1:
            return False,tuple(buffer)
    return True,tuple(buffer)

def gcd(*args):
    """НОД, Попарная проверка"""
    if len(args) > 1:
        if len(args) == 2:
            a = args[0]
            b = args[1]
            while b:
                a, b = b, a % b
            return a
        else:
            result = []
            for i in range(len(args)-1):
                a = args[i]
                for j in range(i+1,len(args)):
                    b = args[j]
                    result.append(gcd(a,b))
            return result
    else:
        raise TypeError('NOD() takes exactly 2 or more arguments(%s given)'% len(args))

def lcm(*args):
    """НОК"""
    if len(args) > 1:
        result = int(args[0]*args[1] / gcd(args[0],args[1]))
        if len(args) == 2:
                return result
        else:
            for i in range(2,len(args)):
                result = lcm(result,args[i])
            return result
    else:
        raise TypeError('lcm takes exactly 2 or more arguments(%s given)'% len(args))

def inv_mod(e,mod):
    return pow(e,euler(mod)-1,mod)

def text_to_int(text,start_index=0,mod=None):
    if type(text) != str:
        raise TypeError('1st argument must be string')

    if type(start_index) != int:
        raise TypeError('2nd argument must be integer')
    elif start_index < 0:
        raise ValueError('2nd argument must be greater than -1')

    if mod:
        if type(mod) != int:
            raise TypeError('3rd argument must be integer')
        elif mod <= 0:
            raise ValueError('3rd argument must be greater than 0')

    Int = []
    for letter in text:
        buff = ord(letter.lower()) - ord('а') + start_index
        if buff >= 0: Int.append(buff)

    if mod:
        z = ''
        target = []
        string = ''.join(str(a) for a in Int)
        for i,char in enumerate(string):
            if int(z + char) < mod:
                z += char
            else:
                target.append(int(z))
                z = char
            if i == len(string)-1:
                target.append(int(z))
    else:
        target = Int
    return target

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
    sqrtN = int(pow(n,0.5)) + 1
    if n % 2 == 0:
        return False
    for divider in range(3,sqrtN,2):
        if n % divider == 0:
            return False
    return True
