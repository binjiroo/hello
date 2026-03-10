import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='horizontal')

        # Kivy side
        kivy_layout = BoxLayout(orientation='vertical')
        kivy_layout.add_widget(Label(text='Kivy Side'))
        kivy_layout.add_widget(TextInput())
        kivy_layout.add_widget(Button(text='Kivy Button'))

        # JavaFX side (Launch the JAR file)
        subprocess.Popen(['java', '-jar', 'YouTubePlayerApp.jar'])

        layout.add_widget(kivy_layout)
        return layout

if __name__ == '__main__':
    MainApp().run()
