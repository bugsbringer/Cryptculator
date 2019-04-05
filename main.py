from kivy.app import App
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

#Config.set('graphics', 'resizable', '0')
#Config.set('graphics', 'width', '360')
#Config.set('graphics', 'height', '640')

class CalculatorApp(App):
    def build(self):
        mainbox = BoxLayout(orientation='vertical',padding=1)
        
        AppW = int(Config.get('graphics', 'width'))
        AppH = int(Config.get('graphics', 'height'))

        fontsize = 72

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
            Button(text = 'φ(x)',   on_press = self.new_fun),
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
            Button(text = 'НОД', on_press = self.new_fun),

            Button(text = '+',   on_press = self.add_operation),
            Button(text = '7',   on_press = self.add_number),
            Button(text = '8',   on_press = self.add_number),
            Button(text = '9',   on_press = self.add_number),
            Button(text = '( )', on_press = self.new_fun),

            Button(text = '-', on_press = self.add_operation),
            Button(text = ',', on_press = self.add_operation),
            Button(text = '0', on_press = self.add_number),
            Button(text = '.', on_press = self.add_number),
            Button(text = '=', on_press = self.result)
        ]

        for button in Buttons:
            button.font_size = fontsize
            keyboard.add_widget(button)

        return mainbox

    def updateEntry(self):
        self.label.text = self.entry_status

    def add_number(self,instance):
        if self.entry_status == '0':
            self.entry_status = ''

        lngh = len(self.entry_status)
        if instance.text == '.':
            if len(self.entry_status) == 0:
                self.entry_status = '0'

            elif self.entry_status[lngh-1:lngh] == '.':
                return

        self.entry_status += instance.text
        self.updateEntry()

    def add_operation(self,instance):
        self.entry_status = self.label.text
        buffer = instance.text
        buffer = buffer.replace('x-¹','-¹mod ')

        if self.entry_status == '0':
            return

        lngh = len(self.entry_status)
        operations = ['+','-','÷','×',',','^','mod ']
        for oprtn in operations:
            if self.entry_status[lngh-len(oprtn):lngh] == oprtn:
                return

        self.entry_status += buffer
        self.updateEntry()

    def result(self,instance):
        buffer = self.entry_status
        buffer = buffer.replace(' mod ','%')
        buffer = buffer.replace('×','*')
        buffer = buffer.replace('÷','/')
        buffer = buffer.replace('^','**')

        try:
            self.entry_status = eval(buffer)

        except Exception as e:
            self.entry_status = 'Ошибка'
        else:
            if self.entry_status == int(self.entry_status):
                self.entry_status = int(self.entry_status)
            self.entry_status = str(self.entry_status)


        if self.entry_status != self.label.text:
            self.updateEntry()
            self.entry_status = '0'

    def new_fun(self,instance):
        print("Клавиша '%s' в разработке." % instance.text)
        pass

    def delete(self,instance):
        lngh = len(self.entry_status)
        exeptions = ['-¹mod ',' mod ']
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
