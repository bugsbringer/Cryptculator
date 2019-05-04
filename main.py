__version__ = '0.3.1'
from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.properties import *

DEBUG = False
if DEBUG:
    try:
        import android
    except ImportError:
        from kivy.config import Config
        from kivy.core.window import Window
        Config.set('graphics', 'resizable', '0')
        Window.size = (306, 544)

X = 0
Y = 1
O = (0,0)

class CustomTextInput(TextInput):
    use_bubble = True

    def on_focus(self, instance, value):
        if self.text == 'p(a,b)':
            self.text = ''

    def insert_text(self, substring, from_undo=False):
        pat = '0123456789(),-'
        if substring in pat:
            s = substring
        else:
            s = ''
        return super(CustomTextInput, self).insert_text(s, from_undo=from_undo)

class CustomDropDown(DropDown):
    data = StringProperty("")
    acts = ['+','-','×']
    pass

class CustomToggleButton(ToggleButton):
    can_color = ListProperty([1, 0.2, 0.1, 0])

    def on_state(self, instance, value):
        if value == 'down':
            self.can_color[3] = 1
            self.color = self.can_color
        else:
            self.can_color[3] = 0
            self.color = 1,1,1,1

class CustomButton(Button):
    __events__ = ('on_long_press', )
    functions = ListProperty(['','',''])
    cur_func = NumericProperty(0)
    funcs_colors = ListProperty([(.5,.15,.6,1),
                                (.75, .16, .23, 1),
                                (.34,.83,.56,1),])
    long_press_time = NumericProperty(1)

    def on_state(self, instance, value):
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        pass

class Row(BoxLayout):
    fs = NumericProperty()
    lable_text = StringProperty("")

class Crypto:
    def isnum(n):
        try:
            n = float(n)
        except Exception as e:
            return False
        else:
            return True

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

        sqrtN = int(pow(n,0.5))+1
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

    def Euler_func(n):
        n = int(n)
        if n > 1:
            dividers = Crypto.factorization(n)[0]
            if not dividers:
                return n - 1
            else:
                buf = 1
                for divider in dividers:
                    buf *= 1 - 1/divider
                return round(n * buf)
        elif n == 1: return 1
        else: return None

    def InvMod(e,mod):
        return pow(e,Crypto.Euler_func(mod)-1,mod)

    def NOD(*args):
        """Попарная проверка"""
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
                        result.append(Crypto.NOD(a,b))
                return result

    def NOK(*args):
        if len(args) > 1:
            result = abs(args[0]*args[1]) // Crypto.NOD(args[0],args[1])
            if len(args) == 2:
                    return result
            else:
                for i in range(2,len(args)):
                    result = Crypto.NOK(result,args[i])
                return result
        else:
            raise TypeError('NOK() takes exactly 2 or more arguments(%s given)'% len(args))

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

        new = [0,0]
        if self.p == 2:
            lam = ((Q[Y] + P[Y]) * Crypto.InvMod(Q[X] + P[X], self.p)) % self.p
            new[X] = lam**2 + P[X] + Q[X]
            new[Y] = lam * (P[X] + new[X]) + P[Y] + self.a
        else:
            lam = ((Q[Y] - P[Y]) * Crypto.InvMod(Q[X] - P[X], self.p)) % self.p
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

        new = [0,0]
        if self.p == 2:
            new[X] = ((P[X]**4 + self.b**2) * Crypto.InvMod(self.a**2,self.p)) % self.p
            lam = (P[X]**2 + self.b) * Crypto.InvMod(self.a,self.p)
            new[Y] = lam * (P[X] + new[X]) + P[Y] + self.a

        if self.p == 3:
            lam = ((self.a*P[X]**2 - self.b) * Crypto.InvMod(P[Y],self.p)) % self.p
            new[X] = lam**2 - self.a + P[X]
            new[Y] = lam*(P[X] - new[X]) - P[Y]

        else:
            lam = ((3*P[X]**2 + self.a) * Crypto.InvMod(2*P[Y],self.p)) % self.p
            new[X] = lam**2 - 2*P[X]
            new[Y] = lam*(P[X] - new[X]) - P[Y]

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
        if n == 0:
            return O
        elif n == 1:
            return P
        elif n == 2:
            return self.double(P)

        bits = list(bin(n)[2:])
        bits.reverse()
        powers = [i for i in range(len(bits)) if bits[i] == '1']

        result = P
        for i in range(powers[0]):
            result = self.double(result)

        for power in powers[1:]:
            buffer = P
            for i in range(power):
                buffer = self.double(buffer)
            result = self.sum(result,buffer)

        return result

    def invert(self, P):
        """P(x1,y1) = P(x1,-y1)"""
        if type(P) != tuple:
            raise TypeError('1st argument be a tuple')
        return (P[X],((-P[Y]) % self.p))

    def order(self,P):
        n = 2
        while True:
            if self.mult(P,n) == O:
                return n
            n += 1

    def isSingular(self):
        D = (4*self.a**3 + 27*self.b**2) % self.p
        if D != 0 and self.p != 2 and self.p != 3:
            return False
        else:
            return True

    def __str__(self):
        if self.a > 0:
            a = ' + '+str(self.a)+'x'
        elif self.a < 0:
            a = ' - '+str(abs(self.a))+'x'
        else:
            a = ''

        if self.b > 0:
            b = ' + '+str(self.b)
        elif self.b < 0:
            b = ' - '+str(abs(self.b))
        else:
            b = ''

        return "E"+str(self.p)+str((self.a,self.b))+": y^2 = x^3"+a+b+" (mod "+str(self.p)+")"

class Elliptic(BoxLayout):
    actions = ['+','-','×']
    def parse_curve_data(self):
        def junk(string):
            list(string)
            numb = ''
            symbl = ''
            new = []
            for i in range(len(string)):
                try: int(numb+string[i])
                except ValueError:
                    if numb:
                        new.append(numb)
                        numb = ''
                    symbl += string[i]
                    if i == len(string)-1:
                        new.append(symbl)
                else:
                    if symbl:
                        new.append(symbl)
                        symbl = ''
                    numb += string[i]
                    if i == len(string)-1:
                        new.append(numb)
            i = 0
            while i < len(new):
                if new[i] == '.':
                    if new[i-1].isdigit():
                        if new[i+1] and new[i+1].isdigit():
                            new[i] += new.pop(i+1)
                            new[i-1] += new.pop(i)
                            i -= 1
                        else:
                            new.pop(i)
                            i -= 1
                i += 1
            i = 0
            while i < len(new):
                l = len(new[i])
                if new[i][l-1:l] == '-':
                    if i == 0:
                        new[i] += new.pop(i+1)
                    elif new[i][l-2] == '(':
                        new[i] = new[i][:l-1]
                        new[i+1] = '-'+new[i+1]
                i += 1

            return new
        data = junk(self.curve_data.text)
        if len(data) != 6 and len(data) != 5:
            return False
        for i in range(0,len(data),2):
            if not Crypto.isdigit(data[i]):
                return False
        p = int(data[0])
        a = int(data[2])
        b = int(data[4])
        return (a,b),p

    def curve_data_focus(self, instance):
        if instance.focused:
            instance.foreground_color = [0,0,0,1]
            if instance.text == 'p(a,b)':
                instance.text = ''
        elif instance.text == '':
                instance.foreground_color = [0,0,0,.5]
                instance.text = 'p(a,b)'

    def input1_focus(self, instance):
        if instance.focused:
            instance.foreground_color = [0,0,0,1]
            if instance.text == 'x,y' or instance.text == 'n':
                instance.text = ''
        elif instance.text == '':
            instance.foreground_color = [0,0,0,.5]
            if self.action.text == self.actions[2]:
                tmp = self.input2.text
                if tmp.isdigit() or tmp == 'n':
                    instance.text = 'x,y'
                else:
                    instance.text = 'n'
            else:
                if instance.text == '':
                    instance.text = 'x,y'

    def input2_focus(self, instance):
        if instance.focused:
            instance.foreground_color = [0,0,0,1]
            if instance.text == 'x,y' or instance.text == 'n':
                instance.text = ''
        elif instance.text == '':
            instance.foreground_color = [0,0,0,.5]
            if self.action.text == self.actions[2]:
                tmp = self.input1.text
                if tmp.isdigit() or tmp == 'n':
                    instance.text = 'x,y'
                else:
                    instance.text = 'n'
            else:
                if instance.text == '':
                    instance.text = 'x,y'

    def on_dropdown_select(self,instance):
        setattr(self.action, 'text', instance.data)

        self.input1.focused = True
        self.input1_focus(self.input1)
        self.input1.focused = False

        self.input2.focused = True
        self.input2_focus(self.input2)
        self.input2.focused = False

    def result(self):
        self.result_input.text = ''

        if type(self.parse_curve_data()) != tuple:
            self.result_input.text = 'Ошибка'
            return

        ab,p = self.parse_curve_data()

        try:
            E = EllipticCurve(ab,p)
            in1 = eval(self.input1.text)
            in2 = eval(self.input2.text)
        except Exception as e:
            self.result_input.text = 'Ошибка'
            return

        action = self.action.text

        if type(in1) != tuple and type(in2) != tuple:
            self.result_input.text = 'Ошибка'
            return

        elif action == self.actions[2]:
            if type(in1) == tuple and type(in2) == tuple:
                self.result_input.text = 'Ошибка'
                return

            elif type(in1) == tuple:
                P = in1
                n = in2

            else:
                n = in1
                P = in2

            result = E.mult(P,n)

        elif action == self.actions[0] or action == self.actions[1]:
            if type(in1) == int or type(in2) == int:
                self.result_input.text = 'Ошибка'
                return
            P = in1
            Q = in2
            if action == self.actions[0]:
                result = E.sum(P,Q)
            else:
                result = E.sub(P,Q)

        self.result_input.text = str(result)

class Usual(BoxLayout):
    entry_status = '0'
    operations = ['+','-','÷','×',',','^','mod ']
    entry_height = 0

    def updateEntry(self):
        if not self.entry_height:
            self.entry_height = self.entry.height
        if self.entry_status == '' or self.entry_status == '()':
            self.entry_status = '0'
        self.entry.text = self.entry_status

        l = self.entry.texture_size[0]/(len(self.entry.text)*self.entry.texture_size[1])
        if l < 0.7:
            if self.entry.font_size > self.entry_height/1.35:
                self.entry.font_size = self.entry.font_size//1.05
        else:
            self.entry.font_size = self.entry_height

    def add_to_story(self):
        self.story.add_widget(Row(lable_text=str(self.entry.text),
                            fs=int(int(self.entry_height)//1.6) ))

    def add_number(self,instance):
        emptys = ['0', 'Ошибка']
        if self.entry_status in emptys:
            self.entry_status = ''

        functions = ['НОД','НОК','φ','F']

        buffer = instance.text
        buffer = buffer.replace('F(N)','F')
        buffer = buffer.replace('φ(x)','φ')

        lngh = len(self.entry_status)
        if instance.text == '.':
            if len(self.entry_status) == 0:
                buffer = '0.'
            else:
                if self.entry_status[lngh-1].isdigit():
                    for i in range(lngh-2,-1,-1):
                        if not self.entry_status[i:lngh-1].isdigit():
                            if self.entry_status[i] == '.':
                                buffer = ''
                            break
                else:
                    if self.entry_status[lngh-1] != '.':
                        buffer = '0.'

        elif buffer in functions:
            if self.entry_status != '':
                if self.entry_status[lngh-1].isdigit():
                    buffer = '×'+buffer+'('
                else:
                    buffer = ''+buffer+'('
            else:
                buffer = ''+buffer+'('

        if lngh > 0 and self.entry_status[lngh-1] == ')':
            self.entry_status += '×'

        self.entry_status += buffer
        self.updateEntry()

    def add_operation(self,instance):
        emptys = ['0', '-','Ошибка']
        self.entry_status = self.entry.text
        if self.entry_status in emptys:
            self.entry_status = ''

        buffer = instance.text
        buffer = buffer.replace('mod',' mod ')
        buffer = buffer.replace('x-¹','-¹mod ')


        if buffer == ',':
            left = self.entry_status.count('(')
            right = self.entry_status.count(')')
            if left-right == 0:
                buffer = ''

        lngh = len(self.entry_status)
        if self.entry_status[lngh-1:lngh] == '.':
            self.entry_status += '0'

        lngh = len(self.entry_status)
        for oprtn in self.operations:
            if self.entry_status[lngh-len(oprtn):lngh] == oprtn:
                self.delete(None)
                break

        lngh = len(self.entry_status)
        if self.entry_status[lngh-1:lngh] == '(':
            if buffer == '-':
                self.entry_status += buffer

        elif self.entry_status != '' or buffer == '-':
            self.entry_status += buffer

        self.updateEntry()

    def EntryParser(self):
        def magic(string):
            def junk(string):
                list(string)
                numb = ''
                symbl = ''
                new = []
                for i in range(len(string)):
                    try: int(numb+string[i])
                    except ValueError:
                        if numb:
                            new.append(numb)
                            numb = ''
                        symbl += string[i]
                        if i == len(string)-1:
                            new.append(symbl)
                    else:
                        if symbl:
                            new.append(symbl)
                            symbl = ''
                        numb += string[i]
                        if i == len(string)-1:
                            new.append(numb)
                i = 0
                while i < len(new):
                    if new[i] == '.':
                        if new[i-1].isdigit():
                            if new[i+1] and new[i+1].isdigit():
                                new[i] += new.pop(i+1)
                                new[i-1] += new.pop(i)
                                i -= 1
                            else:
                                new.pop(i)
                                i -= 1
                    i += 1
                i = 0
                while i < len(new):
                    l = len(new[i])
                    if new[i][l-1:l] == '-':
                        if i == 0:
                            new[i] += new.pop(i+1)
                        elif new[i][l-2] == '(':
                            new[i] = new[i][:l-1]
                            new[i+1] = '-'+new[i+1]
                    i += 1

                return new
            def puck(massive):
                string = ''
                for i in massive:
                    string += i
                return string
            buffer = junk(string)

            i = 0
            while i < len(buffer):
                if buffer[i] == '**' and buffer[i+2] == '%':
                    try:
                        A = int(buffer[i-1])
                        POW = int(buffer[i+1])
                        MOD = int(buffer[i+3])
                    except Exception as e: return 'Ошибка'
                    else: RESULT = pow(A,POW,MOD)
                    buffer[i-1] = str(RESULT)
                    buffer.pop(i)
                    buffer.pop(i)
                    if i == 1:
                        buffer.pop(i)
                        buffer.pop(i)
                    i -= 1

                elif buffer[i] == '-¹mod ':
                    try:
                        E = int(buffer[i-1])
                        MOD = int(buffer[i+1])
                    except Exception as e: return 'Ошибка'
                    else: RESULT = Crypto.InvMod(E,MOD)
                    buffer[i-1] = str(RESULT)
                    for j in range(i+1,i-1,-1):
                        buffer.pop(j)
                    i -= 1

                i += 1

            return puck(buffer)

        while len(self.entry_status)>2 and self.entry_status[len(self.entry_status)-1] == '(':
            self.entry_status = self.entry_status[:len(self.entry_status)-2]

        left = self.entry_status.count('(')
        right = self.entry_status.count(')')
        self.entry_status += ')'*(left-right)
        self.updateEntry()

        string = self.entry_status

        result = string
        result = result.replace(' mod ','%')
        result = result.replace('×','*')
        result = result.replace('÷','/')
        result = result.replace('^','**')
        result = result.replace('НОД','Crypto.NOD')
        result = result.replace('НОК','Crypto.NOK')
        result = result.replace('φ','Crypto.Euler_func')
        result = result.replace('F','Crypto.factorization')

        exeptions = ['Crypto.Euler_func','Crypto.NOD','Crypto.NOK','Crypto.factorization']

        if '(' in result and ')' in result:
            END = result.find(')')
            STRT = result[:END].rfind('(')
            while '(' in result and ')' in result:
                buffer = result[STRT+1:END]
                FUNC_BEFORE = ''
                for e in exeptions:
                    if result[STRT-len(e):STRT] == e:
                        FUNC_BEFORE = e
                        break

                if '-¹mod ' in buffer or ('**' in buffer and '%' in buffer):
                    buffer = magic(buffer)

                try:
                    if FUNC_BEFORE:
                        buffer = FUNC_BEFORE+'('+buffer+')'
                        if FUNC_BEFORE == 'Crypto.factorization':
                            return eval(buffer)

                    elif ',' in buffer:
                        return 'Ошибка'
                    tmp = eval(buffer)

                    if Crypto.isint(tmp):
                        tmp = int(tmp)
                    buffer = str(tmp)

                except Exception as e:
                    END = result[END+1:].find(')')
                    STRT = result[:STRT].rfind('(')
                else:
                    result = result[:STRT-len(FUNC_BEFORE)]+buffer+result[END+1:]

                    END = result.find(')')
                    STRT = result[:END].rfind('(')

                if END == -1 or STRT == -1:
                    break

        if '-¹mod ' in result or ('**' in result and '%' in result):
            result = magic(result)

        return result

    def result(self,instance):
        def fact_handle(tmp):
            dividers,degrees = tmp
            result = ''
            for i in range(len(degrees)):
                if degrees[i] > 1:
                    result += str(dividers[i])+'^'+str(degrees[i])+', '
                else:
                    result += str(dividers[i])+', '
            if result:
                result = result[:len(result)-2]
            else:
                result = 'Простое число'
            return result

        buffer = self.EntryParser()

        if type(buffer) == tuple:
            self.entry_status = fact_handle(buffer)
        else:
            try:
                self.entry_status = eval(buffer)

            except Exception as e:
                self.entry_status = 'Ошибка'
            else:

                    if Crypto.isint(self.entry_status):
                        self.entry_status = int(self.entry_status)

                    self.entry_status = str(self.entry_status)


        if self.entry_status != self.entry.text:
            self.add_to_story()
            self.updateEntry()
            self.entry_status = '0'

    def add_parentheses(self,instance):
        emptys = ['0', 'Ошибка']
        if self.entry_status in emptys:
            self.entry_status = ''

        buffer = ''
        left = self.entry_status.count('(')
        right = self.entry_status.count(')')
        lngh = len(self.entry_status)

        if self.entry_status == '':
            buffer = '('

        elif self.entry_status[lngh-1].isdigit():
            if left - right > 0:
                buffer = ')'
            else:
                buffer = '×('

        elif self.entry_status[lngh-1] == ')':
            if left - right == 0:
                buffer = '×('
            else:
                buffer = ')'

        elif self.entry_status[lngh-1] == '(':
            buffer = '('

        else:
            buffer = '('

        self.entry_status += buffer
        self.updateEntry()

    def switch_key(self,instance):
        count = len(instance.functions)-instance.functions.count('')
        instance.cur_func = ((instance.cur_func + 1) % count)
        self.delete(None)

    def delete(self,instance):
        lngh = len(self.entry_status)
        exeptions = ['-¹mod ',' mod ','НОД(','НОК(','φ(','pow(','F(']
        deleted = False
        for e in exeptions:
            if self.entry_status[lngh-len(e):lngh] == e:
                self.entry_status = self.entry_status[0:lngh-len(e)]
                deleted = True
                break

        if not deleted:
            self.entry_status = self.entry_status[0:lngh-1]

        self.updateEntry()

    def clean(self,instance):
        if self.entry.text == '0':
            self.story.clear_widgets()
        else:
            self.entry_status = '0'
            self.updateEntry()

class RootWidget(BoxLayout):
    def __init__(self):
        super().__init__()
        self.screens = ['Обычный','Эллиптический']

    def switch_screen(self,instance):
        trans = {   self.screens[0]:'right',
                    self.screens[1]:'left'  }
        self.manager.transition.direction = trans[instance.text]
        self.manager.current = instance.text

if __name__ == '__main__':
    runTouchApp(Builder.load_string(open("main.kv", encoding='utf-8').read()))
