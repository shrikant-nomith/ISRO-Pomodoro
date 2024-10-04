from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from datetime import datetime
import csv
import os

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15
reps = 0
daily_log_file = "pomodoro_log.csv"


class IsroPomodoro(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        
        self.logo = Image(source='isro-removebg-preview.png', size_hint=(1, 1))
        self.layout.add_widget(self.logo)

        self.timer_label = Label(text="WORK TIMER", font_size=40, color=[0, 1, 1, 1])
        self.layout.add_widget(self.timer_label)

        self.time_display = Label(text="25:00", font_size=60)
        self.layout.add_widget(self.time_display)

        self.start_button = Button(text="Start", size_hint=(1, 0.2))
        self.start_button.bind(on_press=self.start_timer)
        self.layout.add_widget(self.start_button)

        self.reset_button = Button(text="Reset", size_hint=(1, 0.2))
        self.reset_button.bind(on_press=self.reset_timer)
        self.layout.add_widget(self.reset_button)

        self.graph_button = Button(text="Show Graph", size_hint=(1, 0.2))
        self.graph_button.bind(on_press=self.plot_graph)
        self.layout.add_widget(self.graph_button)

        return self.layout

    def start_timer(self, instance):
        global reps
        reps += 1
        work_sec = WORK_MIN * 60
        short_break_sec = SHORT_BREAK_MIN * 60
        long_break_sec = LONG_BREAK_MIN * 60

        if reps % 8 == 0:
            self.count_down(long_break_sec)
            self.timer_label.text = "BREAK"
        elif reps % 2 == 0:
            self.count_down(short_break_sec)
            self.timer_label.text = "BREAK"
        else:
            self.count_down(work_sec)
            self.timer_label.text = "WORK"

    def reset_timer(self, instance):
        global reps
        reps = 0
        Clock.unschedule(self.update_timer)
        self.time_display.text = "25:00"
        self.timer_label.text = "TIMER"

    def count_down(self, count):
        self.remaining_time = count
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        if self.remaining_time > 0:
            mins, secs = divmod(self.remaining_time, 60)
            self.time_display.text = f"{mins:02}:{secs:02}"
            self.remaining_time -= 1
        else:
            Clock.unschedule(self.update_timer)
            if reps % 2 != 0:
                self.record_work_time(WORK_MIN)
            self.start_timer(None)

    def record_work_time(self, minutes):
        today = datetime.now().strftime("%Y-%m-%d")
        file_exists = os.path.isfile(daily_log_file)
        with open(daily_log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Date", "Minutes"])
            writer.writerow([today, minutes])

    def plot_graph(self, instance):
        import matplotlib.pyplot as plt

        if not os.path.isfile(daily_log_file):
            return

        dates = []
        minutes = {}

        with open(daily_log_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                date = row['Date']
                minutes_spent = int(row['Minutes'])
                if date in minutes:
                    minutes[date] += minutes_spent
                else:
                    minutes[date] = minutes_spent

        dates = list(minutes.keys())
        work_minutes = list(minutes.values())

        plt.figure(figsize=(9, 3))
        plt.bar(dates, work_minutes, color='skyblue')
        plt.xlabel('Date')
        plt.ylabel('Minutes Spent Working')
        plt.title('Daily Pomodoro Work Minutes')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    IsroPomodoro().run()
