import crypto

X = 0
Y = 1
O = (0, 0)


def LegendreSymbol(a, p):
    a = a % p
    if a == 0 or a == 1:
        return a
    if a % 2 == 1:
        return round(pow(-1, (p - 1) * (a - 1) / 4) * LegendreSymbol((p % a), a))
    else:
        return round(pow(-1, (p**2 - 1) / 8) * LegendreSymbol((a / 2), p))


class EllipticCurve:
    def __init__(self, ab, p):
        if type(ab) != tuple:
            raise TypeError('1st argument must be a tuple')

        if type(p) != int:
            raise TypeError('2nd argument must be a integer')

        if p <= 1:
            raise ValueError('2nd argument must be greater than 1')

        self.a, self.b = ab
        self.p = p

    def sum(self, P, Q):
        """(x1,y1) + (x2,y2) = (x3,y3)"""
        if type(P) != tuple:
            raise TypeError('1st argument must be a tuple')
        elif type(Q) != tuple:
            raise TypeError('2nd argument must be a tuple')

        if P == O:
            return Q
        elif Q == O:
            return P

        if P == self.invert(Q):
            return O
        elif P == Q:
            return self.double(P)

        new = [0, 0]
        if self.p == 2:
            lam = ((Q[Y] + P[Y]) * crypto.inv_mod(Q[X] + P[X], self.p)) % self.p
            new[X] = lam**2 + P[X] + Q[X]
            new[Y] = lam * (P[X] + new[X]) + P[Y] + self.a
        else:
            lam = ((Q[Y] - P[Y]) * crypto.inv_mod(Q[X] - P[X], self.p)) % self.p
            if self.p == 3:
                new[X] = lam**2 - P[X] - Q[X] - self.a
            else:
                new[X] = lam**2 - P[X] - Q[X]
            new[Y] = lam * (P[X] - new[X]) - P[Y]

        new[X] = new[X] % self.p
        new[Y] = new[Y] % self.p
        return tuple(new)

    def sub(self, P, Q):
        """(x1,y1) - (x2,y2) = (x3,y3)"""
        return self.sum(P, self.invert(Q))

    def double(self, P):
        """2(x1,y1) = (x3,y3)"""
        if type(P) != tuple:
            raise TypeError('1st argument must be a tuple')
        if P == O:
            return O

        new = [0, 0]
        if self.p == 2:
            new[X] = ((P[X]**4 + self.b**2) * crypto.inv_mod(self.a**2, self.p)) % self.p
            lam = (P[X]**2 + self.b) * crypto.inv_mod(self.a, self.p)
            new[Y] = lam * (P[X] + new[X]) + P[Y] + self.a

        if self.p == 3:
            lam = ((self.a * P[X]**2 - self.b) * crypto.inv_mod(P[Y], self.p)) % self.p
            new[X] = lam**2 - self.a + P[X]
            new[Y] = lam * (P[X] - new[X]) - P[Y]

        else:
            lam = ((3 * P[X]**2 + self.a) * crypto.inv_mod(2 * P[Y], self.p)) % self.p
            new[X] = lam**2 - 2 * P[X]
            new[Y] = lam * (P[X] - new[X]) - P[Y]

        new[X] = new[X] % self.p
        new[Y] = new[Y] % self.p

        return tuple(new)

    def mult(self, P, n):
        """n*P(x1,y1) = R(x3,y3)"""
        if type(P) != tuple:
            raise TypeError('1st argument must be a tuple')
        if type(n) != int:
            raise TypeError('2nd argument must be integer')

        if n < 0:
            n = -n
            P = self.invert(P)
        elif n == 0:
            return O

        bits = list(bin(n)[2:])
        bits.reverse()
        degrees = tuple(i for i in range(len(bits)) if bits[i] == '1')

        muls = [P]
        for i in range(degrees[len(degrees) - 1]):
            muls.append(self.double(muls[i]))

        result = muls[degrees[0]]
        for i in degrees[1:]:
            result = self.sum(result, muls[i])

        return result

    def invert(self, P):
        """P(x1,y1) = P(x1,-y1)"""
        if type(P) != tuple:
            raise TypeError('1st argument be a tuple')
        return (P[X], ((-P[Y]) % self.p))

    def order(self, P):
        n = 2
        while True:
            if self.mult(P, n) == O:
                return n
            n += 1

    def isSingular(self):
        D = (4 * self.a**3 + 27 * self.b**2) % self.p
        if D != 0 and self.p != 2 and self.p != 3:
            return False
        else:
            return True

    def __str__(self):
        if self.a > 0:
            a = ' + ' + str(self.a) + 'x'
        elif self.a < 0:
            a = ' - ' + str(abs(self.a)) + 'x'
        else:
            a = ''

        if self.b > 0:
            b = ' + ' + str(self.b)
        elif self.b < 0:
            b = ' - ' + str(abs(self.b))
        else:
            b = ''

        return "E" + str(self.p) + str((self.a, self.b)) + ": y^2 = x^3" + a + b + " (mod " + str(self.p) + ")"
