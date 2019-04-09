from kivy.app import App
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.uix.recycleview import ScrollView

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

class Row(BoxLayout):
    fs = int(int(Config.get('graphics', 'height'))//22)
    lable_text = StringProperty("")

class Crypt:
    def isint(n):
        try:
            if n == int(n):
                return True
            else:
                return False
        except ValueError:
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

class RootWidget(BoxLayout):
    def __init__(self):
        super().__init__()
        self.entry_status = '0'
        self.operations = ['+','-','÷','×',',','^','mod ']

    def replacer(self,string):
        result = string
        result = result.replace(' mod ','%')
        result = result.replace('×','*')
        result = result.replace('÷','/')
        result = result.replace('^','**')
        result = result.replace('НОД','Crypt.NOD')
        result = result.replace('φ','Crypt.Euler_func')

        while '-¹mod ' in result:
            strt = result.find('-¹mod ')
            endn = strt + len('-¹mod ')

            index = endn
            while index < len(result) and result[index].isdigit():
                index +=1
            try:
                e = eval(result[0:strt])
                mod = eval(result[endn:index])
            except Exception as e:
                result = "Ошибка"
            else:
                result = str(Crypt.InvMod(e,mod)) + result[index:]

        return result

    def updateEntry(self):
        if self.entry_status == '' or self.entry_status == '()':
            self.entry_status = '0'
        self.entry.text = self.entry_status

    def add_number(self,instance):
        if self.entry_status == '0':
            self.entry_status = ''

        buffer = instance.text

        lngh = len(self.entry_status)
        if instance.text == '.':
            if len(self.entry_status) == 0:
                buffer = '0.'

            elif self.entry_status[lngh-1:lngh] == '.':
                return

            else:
                for oprtn in self.operations:
                    if self.entry_status[lngh-len(oprtn):lngh] == oprtn:
                        buffer = '0.'
                        break

        elif instance.text == 'НОД':
            if self.entry_status != '':
                if self.entry_status[lngh-1].isdigit():
                    buffer = '×НОД('
                else:
                    buffer = 'НОД('
            else:
                buffer = 'НОД('

        elif instance.text == 'φ(x)':
            if self.entry_status != '':
                if self.entry_status[lngh-1].isdigit():
                    buffer = '×φ('
                else:
                    buffer = 'φ('
            else:
                buffer = 'φ('

        self.entry_status += buffer
        self.updateEntry()

    def add_operation(self,instance):
        self.entry_status = self.entry.text
        if self.entry_status == '0' or self.entry_status == '-' or self.entry_status == 'Ошибка':
            self.entry_status = ''

        buffer = instance.text
        buffer = buffer.replace('x-¹','-¹mod ')

        if buffer == ',':
            if '(' not in self.entry_status:
                buffer = ''

        lngh = len(self.entry_status)

        if self.entry_status[lngh-1:lngh] == '^' and buffer == ' mod ':
            self.delete(None)
            A = ''
            for i in range(len(self.entry_status)-1,-1,-1):
                if self.entry_status[i].isdigit() or self.entry_status[i] == '.':
                    A += self.entry_status[i]
                else: break
            A = A[::-1]
            cut = self.entry_status.rfind(A)
            self.entry_status = self.entry_status[:cut]
            self.entry_status += 'pow('+A+','
            buffer = ''
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

    def result(self,instance):
        buffer = self.replacer(self.entry_status)

        left = 0
        right = 0
        for i in range(len(self.entry_status)):
            if self.entry_status[i] == '(':
                left +=1
            elif self.entry_status[i] == ')':
                right +=1

        buffer += ')'*(left-right)

        try:
            self.entry_status = eval(buffer)

        except Exception as e:
            self.entry_status = 'Ошибка'
        else:
            try:
                if Crypt.isint(self.entry_status):
                    self.entry_status = int(self.entry_status)
            except Exception as e: None

            self.entry_status = str(self.entry_status)

        if self.entry_status != self.entry.text:
            self.add_to_story()
            self.updateEntry()
            self.entry_status = '0'

    def add_parentheses(self,instance):
        buffer = ''
        left = 0
        right = 0
        lngh = len(self.entry_status)
        for i in range(lngh):
            if self.entry_status[i] == '(':
                left +=1
            elif self.entry_status[i] == ')':
                right +=1

        if self.entry_status[lngh-1].isdigit():
            if left - right > 0:
                strt = self.entry_status.rfind('(') + 1
                endn = self.entry_status[strt:].find(')')
                if endn == -1: endn = lngh
                if self.entry_status[strt-2] != 'φ':
                    try:
                        tmp = self.replacer(self.entry_status[ strt : endn ])
                        eval_result = str(eval(tmp)) != tmp

                    except Exception as e:
                        raise
                    else:
                        if eval_result:
                            buffer = ')'
                        else:
                            buffer = '×('
                else:
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
            for oprtn in self.operations:
                if self.entry_status[lngh-len(oprtn):lngh] == oprtn:
                    buffer = '('
                    break

        self.entry_status += buffer
        self.updateEntry()

    def delete(self,instance):
        lngh = len(self.entry_status)
        exeptions = ['-¹mod ',' mod ','НОД(', 'φ(','pow(']
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

    def add_to_story(self):
        self.story.add_widget(Row(lable_text=str(self.entry.text)))

class MyApp(App):
    def build(self):
        root = Builder.load_string(open("main.kv", encoding='utf-8').read())
        return root

if __name__ == '__main__':
    MyApp().run()
