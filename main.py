__version__ = '0.3.1'
github_version = ''

from kivy.clock import Clock
from kivy.properties import *
from kivy.base import runTouchApp
from kivy.factory import Factory
from kivy.lang.builder import Builder

from kivy.core.clipboard import Clipboard
from kivy.storage.dictstore import DictStore
from kivy.network.urlrequest import UrlRequest

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout

from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.recycleview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen


from plyer import storagepath
from plyer import filechooser

#for DEBUG:
try:
    import android
except ImportError:
    android = None
    from kivy.core.window import Window
    Window.size = (306, 544)
else:
    from jnius import autoclass
    from plyer.platforms.android import activity

#my local modules
from elliptic import EllipticCurve
import crypto
import tools

store = DictStore("cryptculatorapp.data")


def check_version(request, result):
    global github_version, HAVE_UPDATE
    github_version = str(result)

version_url = "https://raw.githubusercontent.com/bugsbringer/Cryptculator-actual-APK/master/version.txt"
ver_request = UrlRequest(version_url, verify=False, on_success=check_version )
ver_request.wait(1)


def open_update_window(event):
    UpdatePopup(cur_version = __version__,git_version = github_version).open()


class UpdatePopup(Popup):
    cur_version = StringProperty("")
    git_version = StringProperty("")


    def download(self, instance):
        instance.disabled = True
        instance.text = 'Загрузка'
        self.file_path = storagepath.get_downloads_dir()+'/cryptculatorapp.apk'

        url = "https://raw.githubusercontent.com/bugsbringer/Cryptculator-actual-APK/master/cryptculatorapp.apk"

        self.request = UrlRequest(url,on_success=self.success,
                                on_failure=self.fail,on_redirect=self.redirect,
                                on_progress=self.downloading, verify=False,
                                file_path=self.file_path, chunk_size=1024*1024)

    def setup_app(self, instance):
        instance.disabled = True
        instance.text = 'Готово'
        if android:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            File = autoclass('java.io.File')
            apkFile = File(self.file_path)

            intent = Intent()
            intent.setAction(Intent.ACTION_INSTALL_PACKAGE)
            intent.setData(Uri.fromFile(apkFile))

            activity.startActivity(intent)

        self.dismiss()

    def success(self, request, result):
        self.action_button.disabled = False
        self.action_button.text = 'Установить'
        self.action_button.bind(on_release=self.setup_app)

    def redirect(self, request, result):
        self.action_button.text = 'redirect'

    def fail(self, request, result):
        self.action_button.text = 'fail'

    def error(self, request, error):
        self.action_button.text = 'error'

    def downloading(self,request, current_size, total_size):
        percent = current_size*100//total_size
        self.progressbar.value = percent

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
        self.text = text[:x]+data+text[x:]
        setattr(self,'cursor',((len(data)+x),self.cursor[1]))

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

    def on_create(self):
        for id in self.ids:
            if store.exists(id):
                self.ids[id].text = store.get(id)['value']

    def inputs_update(self):
        store.put('curve_data',value=self.curve_data.text)
        store.put('input1',value=self.input1.text)
        store.put('input2',value=self.input2.text)
        store.put('action',value=self.action.text)

        self.input1.hint_text = 'x,y'

        if self.action.text == self.actions[2]:
            self.input2.hint_text = 'n'

            if not self.input1.text or not self.input2.text:
                if self.input1.text and crypto.isdigit(self.input1.text):
                    self.input1.hint_text = 'n'
                    self.input2.hint_text = 'x,y'
                else:
                    self.input1.hint_text = 'x,y'
                    self.input2.hint_text = 'n'
        else:
            self.input2.hint_text = 'x,y'

    def result(self):


        def parse_curve_data():
            data = tools.junk(self.curve_data.text)

            if len(data) < 5 or len(data) > 6:
                return False

            for i in [0,2,4]:
                if not crypto.isdigit(data[i]):
                    return False
                else:
                    data[i] = int(data[i])

            p = data[0]
            a = data[2]
            b = data[4]

            return (a,b),p


        self.result_input.text = ''
        self.result_input.hint_text_color = [1,0,0,.5]
        tmp_parse =  parse_curve_data()
        if type(tmp_parse) != tuple:
            self.result_input.hint_text = 'Ошибка'
            return
        else:
            ab,p = tmp_parse

        try:
            E = EllipticCurve(ab,p)
            in1 = eval(self.input1.text)
            in2 = eval(self.input2.text)
        except Exception as e:
            self.result_input.hint_text = 'Ошибка'
            return

        action = self.action.text

        if type(in1) != tuple and type(in2) != tuple:
            self.result_input.hint_text = 'Ошибка'
            return

        elif action == self.actions[2]:
            if type(in1) == tuple and type(in2) == tuple:
                self.result_input.hint_text = 'Ошибка'
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
                self.result_input.hint_text = 'Ошибка'
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

    def on_create(self):
        #доделать
        None


    def updateEntry(self):
        if self.entry_status == '' or self.entry_status == '()':
            self.entry_status = '0'

        old_len = len(self.entry.text)
        self.entry.text = self.entry_status
        cur_len = len(self.entry.text)

        d = old_len - cur_len
        l = self.entry.texture_size[0]/(cur_len*self.entry.texture_size[1])

        for i in range(abs(d)):
            if self.entry.font_size > self.entry.texture_size[1]/1.4 and d < 0 and l < 0.7:
                self.entry.font_size -= self.entry.texture_size[1]*.05
            elif self.entry.font_size < self.entry.texture_size[1] and d > 0 and l > 0.4:
                self.entry.font_size += self.entry.texture_size[1]*.05
            else:
                break

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
                    elif type(tmp) == float:
                        tmp = round(tmp,10)
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
        if github_version:
            if float(github_version[2:]) > float(__version__[2:]):
                Clock.schedule_once(open_update_window, 3)

    def switch_screen(self,instance):
        trans = {   self.screens[0]:'right',
                    self.screens[1]:'left'  }
        self.manager.transition.direction = trans[instance.text]
        self.manager.current = instance.text

if __name__ == '__main__':
    runTouchApp(Builder.load_string(open("main.kv", encoding='utf-8').read()))
