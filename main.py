__version__ = '0.3.1'

from kivy.clock import Clock
from kivy.properties import *
from kivy.base import runTouchApp
from kivy.core.clipboard import Clipboard
from kivy.lang.builder import Builder

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout

from kivy.uix.dropdown import DropDown
from kivy.uix.recycleview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen

#my local modules
from elliptic import EllipticCurve
import crypto
import tools

#for DEBUG:
try:
    import android
except ImportError:
    from kivy.core.window import Window
    Window.size = (306, 544)

class CustomTextInput(TextInput):


    def copy(self, data=''):
         Clipboard.copy(self.selection_text)

    def cut(self):
        Clipboard.copy(self.selection_text)
        data = self.selection_text
        self.delete_selection()

    def paste(self):
        data = Clipboard.paste()
        text = self.text
        x = self.cursor[0]
        print(self.cursor)
        self.text = text[:x]+data+text[x:]
        print(self.cursor)
        setattr(self,'cursor',((len(data)+x),self.cursor[1]))
        print(self.cursor)

    def insert_text(self, substring, from_undo=False):
        pat = '0123456789(),-'
        if substring in pat:
            s = substring
        else:
            s = ''
        return super(CustomTextInput, self).insert_text(s, from_undo=from_undo)

class ReadOnlyTextInput(CustomTextInput):


    def insert_text(self, substring, from_undo=False):
        return super(ReadOnlyTextInput, self).insert_text('', from_undo=from_undo)

class CustomDropDown(DropDown):
    data = StringProperty("")
    acts = ['+','-','×']


    def open(self,instance):
        for child in self.children[0].children:
            if child.text == instance.text:
                child.height = 0
            else:
                child.height = self.max_height//2
            child.font_size = child.height//1.55
        return super(CustomDropDown, self).open(instance)

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
    long_press_time = NumericProperty(1)

    functions = ListProperty(['','',''])
    cur_func = NumericProperty(0)
    funcs_colors = ListProperty([(.5,.15,.6,1),
                                (.75, .16, .23, 1),
                                (.34,.83,.56,1),])



    def on_state(self, instance, value):
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        count = len(self.functions) - self.functions.count('')
        self.cur_func = ((self.cur_func + 1) % count)
        pass

class Row(BoxLayout):
    fs = NumericProperty()
    lable_text = StringProperty("")

class Elliptic(BoxLayout):
    actions = ['+','-','×']


    def curve_data_focus(self, instance):
        if instance.focused:
            instance.foreground_color = [0,0,0,1]
            if instance.text == 'p(a,b)':
                instance.text = ''
        elif instance.text == '':
                instance.foreground_color = [0,0,0,.5]
                instance.text = 'p(a,b)'

    def input_focus(self, instance):
        if instance == self.input1:
            tmp = self.input2
        elif instance == self.input2:
            tmp = self.input1

        if instance.focused:
            instance.foreground_color = [0,0,0,1]
            if instance.text == 'x,y' or instance.text == 'n':
                instance.text = ''
        else:
            if instance.text == '':
                instance.foreground_color = [0,0,0,.5]
                if self.action.text == self.actions[2]:
                    if tmp.text.isdigit() or tmp.text == 'n':
                        instance.text = 'x,y'
                    else:
                        instance.text = 'n'
                else:
                    if instance.text == '':
                        instance.text = 'x,y'
        if instance.text != '':
            if self.action.text == self.actions[2]:
                if tmp.text == 'x,y' or tmp.text == 'n':
                    tmp.foreground_color = [0,0,0,.5]
                    if instance.text.isdigit() or instance.text == 'n':
                        tmp.text = 'x,y'
                    else:
                        tmp.text = 'n'

    def result_focus(self, instance):
        if instance.focused:
            instance.foreground_color = [0,0,0,1]
            if instance.text == 'Результат' or instance.text == 'Ошибка':
                instance.text = ''
        else:
            if instance.text == '':
                instance.foreground_color = [0,0,0,.5]
                instance.text = 'Результат'

    def on_dropdown_select(self,instance):
        setattr(self.action, 'text', instance.data)

        self.input1.focused = True
        self.input1.focused = False

        self.input2.focused = True
        self.input2.focused = False

    def result(self):


        def parse_curve_data():
            data = tools.junk(self.curve_data.text)
            if len(data) != 6 and len(data) != 5:
                return False
            for i in range(0,len(data),2):
                if not crypto.isdigit(data[i]):
                    return False
            p = int(data[0])
            a = int(data[2])
            b = int(data[4])
            return (a,b),p

        self.result_input.text = ''
        self.result_input.foreground_color = [1,0,0,.5]
        tmp_parse = parse_curve_data()
        if type(tmp_parse) != tuple:
            self.result_input.text = 'Ошибка'
            return

        ab,p = tmp_parse

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
        self.result_input.foreground_color = [0,0,0,1]
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
            buffer = tools.junk(string)
            i = 0
            while i < len(buffer):
                if buffer[i] == '**' and buffer[i+2] == '%':
                    try:
                        A = int(buffer[i-1])
                        POW = int(buffer[i+1])
                        MOD = int(buffer[i+3])
                    except Exception as e:
                        return 'Ошибка'
                    else:
                        RESULT = pow(A,POW,MOD)
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
                    else: RESULT = crypto.inv_mod(E,MOD)
                    buffer[i-1] = str(RESULT)
                    for j in range(i+1,i-1,-1):
                        buffer.pop(j)
                    i -= 1

                i += 1

            return ''.join([char for char in buffer])

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
        result = result.replace('НОД','crypto.gcd')
        result = result.replace('НОК','crypto.lcm')
        result = result.replace('φ','crypto.euler')
        result = result.replace('F','crypto.factorization')

        exeptions = ['crypto.euler','crypto.gcd','crypto.lcm','crypto.factorization']

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
                        if FUNC_BEFORE == 'crypto.factorization':
                            return eval(buffer)

                    elif ',' in buffer:
                        return 'Ошибка'
                    tmp = eval(buffer)

                    if crypto.isint(tmp):
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

                    if crypto.isint(self.entry_status):
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
