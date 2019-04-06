try:
    from kivy.app import App
    from kivy.config import Config
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
except:
    print('Похоже отсутствует библиотека kivy.')
    print('Следующие команды установят все нужные библиотеки(Это не займет много времени):')
    print('python3 -m pip install --upgrade pip wheel setuptools')
    print('python3 -m pip install --upgrade docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew')
    print('python3 -m pip install --upgrade kivy.deps.angle')
    print('python3 -m pip install --upgrade kivy')
    print('Подробная инструкция: https://kivy.org/doc/stable/installation/installation-windows.html')
    input('Нажмите любую клавишу для выхода.')
    exit()

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

def isint(n):
    try:
        if n == int(n):
            return True
        else:
            return False
    except ValueError:
        return False

class Crypt:
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


class CalculatorApp(App):
    def build(self):
        mainbox = BoxLayout(orientation='vertical',padding=1)

        AppW = int(Config.get('graphics', 'width'))
        AppH = int(Config.get('graphics', 'height'))

        fontsize = 24

        self.label = Label( text = '0', font_size=fontsize,
                            halign='right', valign='center',
                            size_hint=(1,.3), text_size=(AppW, AppH*.3) )
        mainbox.add_widget(self.label)

        self.entry_status = '0'

        keyboard = GridLayout(cols=5, size_hint=(1,.7))
        mainbox.add_widget(keyboard)

        Buttons = [
            Button(text = '^',      on_press = self.add_operation),
            Button(text = ' mod ',  on_press = self.add_operation),
            Button(text = 'φ(x)',   on_press = self.add_euler),
            Button(text = 'x-¹',    on_press = self.add_operation),
            Button(text = '<-',     on_press = self.delete),

            Button(text = '×', on_press = self.add_operation),
            Button(text = '1', on_press = self.add_number),
            Button(text = '2', on_press = self.add_number),
            Button(text = '3', on_press = self.add_number),
            Button(text = 'C', on_press = self.clean),

            Button(text = '÷',   on_press = self.add_operation),
            Button(text = '4',   on_press = self.add_number),
            Button(text = '5',   on_press = self.add_number),
            Button(text = '6',   on_press = self.add_number),
            Button(text = 'НОД', on_press = self.add_number),

            Button(text = '+',   on_press = self.add_operation),
            Button(text = '7',   on_press = self.add_number),
            Button(text = '8',   on_press = self.add_number),
            Button(text = '9',   on_press = self.add_number),
            Button(text = '( )', on_press = self.add_parentheses),

            Button(text = '-', on_press = self.add_operation),
            Button(text = ',', on_press = self.add_operation),
            Button(text = '0', on_press = self.add_number),
            Button(text = '.', on_press = self.add_number),
            Button(text = '=', on_press = self.result)
        ]

        for button in Buttons:
            button.font_size = fontsize
            keyboard.add_widget(button)

        self.operations = ['+','-','÷','×',',','^','mod ']

        return mainbox

    def replacer(self,string):
        result = string
        result = result.replace(' mod ','%')
        result = result.replace('×','*')
        result = result.replace('÷','/')
        result = result.replace('^','**')
        result = result.replace('НОД','Crypt.NOD')

        while '-¹mod ' in result:
            strt = result.find('-¹mod ')
            endn = result.find('-¹mod ') + len('-¹mod ')

            index = endn
            while index < len(result) and result[index].isdigit():
                index +=1

            e = eval(result[0:strt])
            mod = eval(result[endn:index])

            result = str(Crypt.InvMod(e,mod)) + result[index:]

        return result

    def updateEntry(self):
        self.label.text = self.entry_status

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

        self.entry_status += buffer
        self.updateEntry()

    def add_operation(self,instance):
        self.entry_status = self.label.text
        buffer = instance.text
        buffer = buffer.replace('x-¹','-¹mod ')

        if self.entry_status == '0':
            return

        lngh = len(self.entry_status)
        for oprtn in self.operations:
            if self.entry_status[lngh-len(oprtn):lngh] == oprtn:
                self.delete(None)
                break

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
            if isint(self.entry_status):
                self.entry_status = int(self.entry_status)

            self.entry_status = str(self.entry_status)

        if self.entry_status != self.label.text:
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
                try:
                    strt = self.entry_status.rfind('(') + 1
                    endn = self.entry_status[strt:].find(')')
                    if endn == -1: endn = lngh

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

    def add_euler(self,instance):
        print("Клавиша '%s' в разработке." % instance.text)
        pass

    def delete(self,instance):
        lngh = len(self.entry_status)
        exeptions = ['-¹mod ',' mod ','НОД(']
        deleted = False
        for e in exeptions:
            if self.entry_status[lngh-len(e):lngh] == e:
                self.entry_status = self.entry_status[0:lngh-len(e)]
                deleted = True
                break

        if not deleted:
            self.entry_status = self.entry_status[0:lngh-1]

        if not self.entry_status:
            self.entry_status = '0'
        self.updateEntry()

    def clean(self,instance):
        self.entry_status = '0'
        self.updateEntry()


if __name__ == '__main__':
    CalculatorApp().run()
