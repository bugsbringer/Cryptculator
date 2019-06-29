import crypto


def take_degrees(dividers):
    degrees = []
    for i, num in enumerate(dividers):
        if num not in dividers[:i]:
            degrees.append(dividers.count(num)) # кол-во одинковых значение -> степень этого значения (2,2,2 -> 2^3)

    dividers = sorted(list(set(dividers))) # убираем повторяюшиеся значения

    return dividers, degrees


def junk(string):
    result = []
    last_is_string = False
    i = 0
    while i < len(string):
        if crypto.isnum(string[i]) or (string[i] == '-'
                                and (i == 0 or string[i-1] == '(')):
            buffer = string[i]
            while i+1 < len(string) and crypto.isnum(buffer + string[i+1]):
                i += 1
                buffer += string[i]
            result.append(buffer)
            last_is_string = False
        else:
            if last_is_string:
                result[len(result)-1] += string[i]
            else:
                result.append(string[i])
                last_is_string = True
        i += 1
    return result


def parse_curve_data(curve_data):
    data = junk(curve_data)

    if len(data) != 6 or (data[1], data[3], data[5]) != ('(', ',', ')'):
        return False

    if any([not crypto.isdigit(data[i]) for i in (0,2,4)]):
        return False

    p = int(data[0])
    a = int(data[2])
    b = int(data[4])

    return (a, b), p


def text_to_int(text, start_index=0, mod=None):
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
        if buff >= 0:
            Int.append(buff)

    if mod:
        z = ''
        target = []
        string = ''.join(str(a) for a in Int)
        for i, char in enumerate(string):
            if int(z + char) < mod:
                z += char
            else:
                target.append(int(z))
                z = char
            if i == len(string) - 1:
                target.append(int(z))
    else:
        target = Int
    return target
