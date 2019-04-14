from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import *
from kivy.uix.recycleview import ScrollView
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '306')
Config.set('graphics', 'height', '544')

class CustomButton(Button):
    __events__ = ('on_long_press', )
    functions = ListProperty(['',''])
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

class Crypt:
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
            dividers = Crypt.factorization(n)[0]
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
        return pow(e,Crypt.Euler_func(mod)-1,mod)

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
                        result.append(Crypt.NOD(a,b))
                return result

    def NOK(*args):
        if len(args) > 1:
            result = int(args[0]*args[1] / Crypt.NOD(args[0],args[1]))
            if len(args) == 2:
                    return result
            else:
                for i in range(2,len(args)):
                    result = Crypt.NOK(result,args[i])
                return result
        else:
            raise TypeError('NOK() takes exactly 2 or more arguments(%s given)'% len(args))

class RootWidget(BoxLayout):
    def __init__(self):
        super().__init__()
        self.entry_status = '0'
        self.operations = ['+','-','÷','×',',','^','mod ']
        self.entry_height = 0

    def updateEntry(self):
        if not self.entry_height:
            self.entry_height = self.entry.height
        if self.entry_status == '':
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
                    else: RESULT = Crypt.InvMod(E,MOD)
                    buffer[i-1] = str(RESULT)
                    for j in range(i+1,i-1,-1):
                        buffer.pop(j)
                    i -= 1

                i += 1

            return puck(buffer)

        if self.entry_status[len(self.entry_status)-1] == '(':
            return self.entry_status

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
        result = result.replace('НОД','Crypt.NOD')
        result = result.replace('НОК','Crypt.NOK')
        result = result.replace('φ','Crypt.Euler_func')
        result = result.replace('F','Crypt.factorization')

        exeptions = ['Crypt.Euler_func','Crypt.NOD','Crypt.NOK','Crypt.factorization']

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
                        if FUNC_BEFORE == 'Crypt.factorization':
                            return eval(buffer)

                    elif ',' in buffer:
                        print('return Ошибка',buffer)
                        return 'Ошибка'
                    tmp = eval(buffer)

                    if Crypt.isint(tmp):
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

                    if Crypt.isint(self.entry_status):
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

class MyApp(App):
    def build(self):
        root = Builder.load_string(open("main.kv", encoding='utf-8').read())
        return root

if __name__ == '__main__':
    MyApp().run()
