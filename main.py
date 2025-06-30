from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
import threading
import time

class NavigationApp(App):
    def build(self):
        Window.clearcolor = (0.9, 0.95, 1, 1)  # Light blue background

        # Route steps with relative image paths
        self.route_steps = [
            {"location": "Start", "instruction": "Head north", "image": "assets/start.png"},
            {"location": "Junction", "instruction": "Turn right", "image": "assets/turn_right.png"},
            {"location": "School Zone", "instruction": "Slow down", "image": "assets/school_zone.png"},
            {"location": "Traffic Light", "instruction": "Prepare to stop", "image": "assets/traffic_light.png"},
            {"location": "Destination", "instruction": "You have arrived", "image": "assets/destination.png"}
        ]

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.image = Image(source=self.route_steps[0]['image'], size_hint=(1, 0.8))
        self.label = Label(text="Starting Navigation...", font_size=28, color=(0, 0, 0, 1), size_hint=(1, 0.2))

        self.layout.add_widget(self.image)
        self.layout.add_widget(self.label)

        threading.Thread(target=self.simulate_navigation, daemon=True).start()
        return self.layout

    def simulate_navigation(self):
        for step in self.route_steps:
            Clock.schedule_once(lambda dt, s=step: self.update_ui(s), 0)
            time.sleep(3)
        Clock.schedule_once(lambda dt: self.label_update("✅ Navigation complete."), 0)

    def update_ui(self, step):
        self.image.source = step['image']
        self.label.text = f"[{step['location']}]\n{step['instruction']}"

    def label_update(self, text):
        self.label.text = text

if __name__ == '__main__':
    NavigationApp().run()
