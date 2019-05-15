__version__ = '0.3.4'
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import *
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
#my local modules
import elliptic
import crypto
import tools

#for DEBUG:
try:
    import android
except ImportError:
    android = None
    from kivy.core.window import Window
    resolution = 16/9
    W = 302
    Window.size = (W, W*resolution)

from plyer import storagepath
if android:
    from jnius import autoclass
    from plyer.platforms.android import activity

store = DictStore("cryptculatorapp.data")
APK_FILE_PATH = storagepath.get_downloads_dir()+'/cryptculatorapp.apk'

class CustomTextInput(TextInput):
    name = StringProperty('')


    def on_text(self, instance, text):
        store.put(self.name,value=text)

    def copy(self, data=''):
         Clipboard.copy(self.selection_text)

    def cut(self):
        Clipboard.copy(self.selection_text)
        self.delete_selection()

    def paste(self):
        data = Clipboard.paste()
        text = self.text
        x = self.cursor[0]
        l = len(self.text) - x
        self.text = text[:x]+data+text[x:]
        self.cursor = (len(self.text) - l,self.cursor[1])

    def insert_text(self, substring, from_undo=False):
        pat = '0123456789(),-'
        if not substring in pat:
            substring = ''
        return super(CustomTextInput, self).insert_text(substring, from_undo=from_undo)

class ReadOnlyTextInput(CustomTextInput):

    def delete_selection(self):
        return

    def do_backspace(self):
        return

    def paste(self):
        return

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
    __events__ = ('on_long_press', 'on_short_press')
    long_press_time = NumericProperty(1)
    is_long_pressed = False
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

    def on_release(self):
        if self.is_long_pressed:
            self.is_long_pressed = False
        else:
            self._do_short_press()


    def _do_short_press(self):
        self.dispatch('on_short_press')

    def on_short_press(self, *largs):
        pass

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        self.is_long_pressed = True
        count = len(self.functions) - self.functions.count('')
        self.cur_func = ((self.cur_func + 1) % count)
        pass

class Row(BoxLayout):
    fs = NumericProperty()
    lable_text = StringProperty("")

class Elliptic(BoxLayout):
    actions = ['+','-','×']

    def on_create(self):
        if store.exists('action'):
            self.ids['action'].text = store.get('action')['value']
        for id in self.ids:
            self.ids[id].name = id
            if store.exists(id):
                self.ids[id].text = store.get(id)['value']
        self.inputs_update()

    def inputs_update(self,a=None,b=None):
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


        self.result_input.text = ''
        if self.input1.text and self.input2.text and self.curve_data.text:
            self.result()
        else:
            self.result_input.hint_text_color = [.5, .5, .5, 1]
            self.result_input.hint_text = 'Результат'

    def result(self):


        def parse_curve_data():
            data = tools.junk(self.curve_data.text)

            if len(data) != 6:
                return False

            if (data[1], data[3], data[5]) != ('(', ',', ')'):
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

        tmp_parse =  parse_curve_data()

        self.result_input.hint_text_color = [1,0,0,.5]

        if not tmp_parse:
            self.result_input.hint_text = 'Ошибка'
            return

        ab,p = tmp_parse

        try:
            E = elliptic.EllipticCurve(ab,p)
            in1 = eval(self.input1.text)
            in2 = eval(self.input2.text)
        except Exception as e:
            self.result_input.hint_text = 'Ошибка'
            return

        action = self.action.text

        if action == self.actions[2]:
            if type(in1) == tuple and type(in2) == tuple:
                self.result_input.hint_text = 'Ошибка'
                return

            elif type(in1) == tuple:
                P = in1
                n = in2

            else:
                n = in1
                P = in2

            if len(P) != 2:
                self.result_input.hint_text = 'Ошибка'
                return

            result = E.mult(P,n)

        elif action == self.actions[0] or action == self.actions[1]:
            if (type(in1) == int or type(in2) == int
                        or len(in1) != 2 or len(in2) != 2):
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

    def updateEntry(self):
        if self.entry_status == '' or self.entry_status == '()':
            self.entry_status = '0'

        self.entry.text = self.entry_status

        self.entry.font_size = self.entry.height
        lenght = len(self.entry.text)

        if lenght > 10:
            for i in range(lenght-10):
                self.entry.font_size -= self.entry.height*.05
                if self.entry.font_size < self.entry.height/1.5:
                    self.entry.font_size = self.entry.height/1.5
                    break

    def add_to_story(self):
        self.story.add_widget(Row(lable_text= self.entry.text,
                                    fs=self.entry.height//1.7 ))

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
            if lngh == 0:
                buffer = '0.'
            else:
                if self.entry_status[lngh-1].isdigit():
                    for i in range(lngh-2,-1,-1):
                        if not self.entry_status[i:lngh-1].isdigit():
                            if self.entry_status[i] == '.':
                                buffer = ''
                            break
                elif self.entry_status[lngh-1] == '.':
                    buffer = ''
                elif self.entry_status[lngh-1] != '.':
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

    def scroll_sizer(self):
        if self.entry.size[0] > self.story.size[0]:
            setattr(self.entry_scroller,'width',self.story.size[0])
        else:
            setattr(self.entry_scroller,'width',self.entry.size[0])

class UpdatePopup(Popup):
    cur_version = StringProperty("")
    git_version = StringProperty("")
    Downloaded = False

    def on_parent(self,instance,value):
        self.info.text = storagepath.get_downloads_dir()

    def download(self):
        if not self.Downloaded:
            self.action_button.disabled = True
            self.action_button.text = 'Загрузка'

            url = "https://raw.githubusercontent.com/bugsbringer/Cryptculator-actual-APK/master/cryptculatorapp.apk"
            self.info.text += '\nЗагрузка...'
            self.request = UrlRequest(url,on_success=self.success,debug=True,
                                    on_failure=self.fail,on_redirect=self.redirect,
                                    on_progress=self.downloading, verify=False,
                                    file_path=APK_FILE_PATH, chunk_size=1024*512)

    def setup_app(self, instance):
        self.info.text += '\nУстановка'
        instance.disabled = True
        instance.text = 'Готово'
        if android:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            File = autoclass('java.io.File')
            apkFile = File(APK_FILE_PATH)

            intent = Intent()
            intent.setAction(Intent.ACTION_INSTALL_PACKAGE)
            intent.setData(Uri.fromFile(apkFile))

            activity.startActivity(intent)

    def success(self, request, result):
        self.Downloaded = True
        self.info.text += '\nЗагрузка завершена.'
        self.action_button.text = 'Установить'
        self.action_button.bind(on_release=self.setup_app)
        self.action_button.disabled = False

    def redirect(self, request, result):
        self.info.text += '\nRedirect: '+str(result)

    def fail(self, request, result):
        self.info.text += '\nFail: '+str(result)

    def error(self, request, error):
        self.info.text += '\nError: '+str(result)

    def downloading(self,request, current_size, total_size):
        percent = current_size*100//total_size
        self.progressbar.value = percent
        self.percent.text = str(percent)+'%'

        self.current_size.text = str(round(current_size/(1024**2),1))+'MB'
        self.total_size.text = str(round(total_size/(1024**2),1))+'MB'

class LastUpdateInfoPopup(Popup):
    information = """[b]Окно информации:[/b]
    [i]Это окно[/i]
    [i]Окно справки[/i]
[b]Малозаметные[/b] [i]улучшения[/i]
[i]Доработана[/i] [b]система обновления[/b]

[b]Калькуляторы:[/b]
  [b]Обычный:[/b]
    - [i]Доработаны[/i] [b]переключаемые[/b] кнопки
    - [b]Скролируемое[/b] [i]поле ввода[/i]
    - [i]Улучшено[/i] скалирование
            шрифта [i]поля ввода[/i]

  [b]Эллиптический:[/b]
    - Расчет при вводе
    - [i]Улучшен[/i] [b]алгоритм умножения[/b]
    """

    def on_open(self):
        store.put('info',value=True)

class AboutPopup(Popup):
    information = """[b]CryptCulator[/b] – учебная программа
для вычислений в области криптологии.
[b]Калькуляторы:[/b]

[b]Обычный:[/b]
  [b]Функции[/b]
    Кнопки с [b]цветовым индикатором[/b], при
    [b]продолжительном[/b] нажатии [i]переключаются[/i]
    к [u]альтернативной функции[/u] :

        [b][color=#86319E]« φ(n) »[/color] / [color=#C23445]« F(N) »[/color][/b] –
            [color=#86319E]Функция Эйлера[/color]
            [color=#C23445]Факторизация числа[/color]

        [b][color=#86319E]« НОД »[/color] / [color=#C23445]« НОК »[/color][/b] –
            [color=#86319E]Наибольший общий делитель[/color]
            [color=#C23445]Наименьшее общее кратное[/color]
            (обе функции принимают 2 и больше
            параметров, НОД выдает массив
                            попарных результатов)

    [b]« ^ »[/b] - Возведение в степень

    [b]« a^b mod p »[/b] - Бинарный алгоритм
            возведения в степень по модулю

    («а^(1/x)» - [u]корень[/u] степени «x» из числа «а»)

    [b]« x-¹ »[/b] – Нахождение обратного
                элемента по модулю

[b]Эллиптической криптографии:[/b]
    [b]p(a, b)[/b] – параметры эллиптической кривой

    [b]х,у[/b] – координаты точек
    [b]n[/b] – множитель (при умножении)

    [b]Функции[/b]
        [i]Вычитание, сложение, умножение[/i]
 """

class SettingsPopup(Popup):
    current_version = __version__

    def check_for_update(self):
        def check_version( request, result):
            self.git_version = str(result)

        def open_update_window(event):
            if self.git_version:
                if float(self.git_version[2:]) > float(__version__[2:]):
                    UpdatePopup(cur_version = __version__,
                                git_version = self.git_version).open()

        version_url = "https://raw.githubusercontent.com/bugsbringer/Cryptculator-actual-APK/master/version.txt"
        ver_request = UrlRequest(version_url, verify=False,
                                    on_success=check_version )

        Clock.schedule_once(open_update_window, 2)

    def open_lastupdinfo_window(self):
        LastUpdateInfoPopup().open()

    def open_about_window(self):
         AboutPopup().open()

class RootWidget(BoxLayout):
    def __init__(self):
        super().__init__()
        self.git_version = ''
        self.check_for_update(time=5)
        self.delete_old_apkfile()
        if not store.exists('info') or store.get('info')['value'] == False:
            Clock.schedule_once(self.open_lastupdinfo_window, 2)
        self.screens = ['Обычный','Эллиптический']

    def open_lastupdinfo_window(self, event):
        InfPop = LastUpdateInfoPopup()
        InfPop.bind(on_dismiss=self.check_for_update)
        InfPop.open()

    def open_settings_popup(self):
        SettingsPopup().open()

    def delete_old_apkfile(self):
        if android:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            File = autoclass('java.io.File')
            apkFile = File(APK_FILE_PATH)
            apkFile.delete()

    def check_for_update(self, event = None, time = 1):
        def check_version( request, result):
            self.git_version = str(result)

        def open_update_window(event):
            if self.git_version:
                if float(self.git_version[2:]) > float(__version__[2:]):
                    UpdatePopup(cur_version = __version__,
                                git_version = self.git_version).open()

        if not self.git_version:
            version_url = "https://raw.githubusercontent.com/bugsbringer/Cryptculator-actual-APK/master/version.txt"
            ver_request = UrlRequest(version_url, verify=False,
                                        on_success=check_version )
        if store.exists('info') and store.get('info')['value'] == True:
            Clock.schedule_once(open_update_window, time)

    def switch_screen(self,instance):
            trans = {   self.screens[0]:'right',
                        self.screens[1]:'left'  }
            self.manager.transition.direction = trans[instance.text]
            self.manager.current = instance.text

class CryptculatorApp(App):
    def build(self):
        return Builder.load_string(open("main.kv", encoding='utf-8').read())

    def on_pause(self):
        return True


if __name__ == '__main__':
    CryptculatorApp().run()
