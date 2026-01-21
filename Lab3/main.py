from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core. window import Window
from kivy. uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
import tkinter as tk
from tkinter import filedialog
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

#Б9123-09.03.04, подгруппа 5
#Producer: Жуков Никита
#Consumer:  Умрилов Егор

Window.size = (900, 650)
Window.clearcolor = (0.15, 0.15, 0.2, 1)
Window.title = "Kafka Data Sender"


class StyledButton(Button):
    def __init__(self, bg_color=(0.3, 0.5, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class KafkaDataSender(App):
    def __init__(self):
        super().__init__()
        self.data_grid = []
        self.columns = 3
        self.rows_count = 0
        self. file_path = None

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                request_timeout_ms=5000,
                max_block_ms=5000
            )
            print("✓ Успешное подключение к Kafka")
        except Exception as e:
            print(f"✗ Ошибка подключения к Kafka: {e}")
            print("⚠ Работа в режиме без Kafka (данные будут сохранены в файл)")
            self.producer = None
            self.producer = None

    def build(self):
        root = FloatLayout()

        title = Label(
            text="KAFKA DATA SENDER",
            font_size=28,
            bold=True,
            color=(0.9, 0.9, 0.95, 1),
            size_hint=(0.6, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.98}
        )
        root.add_widget(title)

        self.table_name_input = TextInput(
            hint_text="Введите название таблицы.. .",
            multiline=False,
            size_hint=(0.4, 0.06),
            pos_hint={'x': 0.05, 'top': 0.88},
            background_color=(0.25, 0.25, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.6, 0.6, 0.6, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[15, 12]
        )
        root.add_widget(self.table_name_input)

        btn_data = [
            ("+ Строка", self.add_row, (0.2, 0.7, 0.4, 1)),
            ("+ Столбец", self.add_column, (0.2, 0.6, 0.5, 1)),
            ("− Строка", self.remove_row, (0.8, 0.3, 0.3, 1)),
            ("− Столбец", self.remove_column, (0.7, 0.25, 0.25, 1)),
            ("Загрузить", self.load_file, (0.5, 0.5, 0.6, 1)),
            ("Очистить", self.clear_table, (0.6, 0.4, 0.2, 1)),
        ]

        for i, (text, callback, color) in enumerate(btn_data):
            btn = StyledButton(
                text=text,
                bg_color=color,
                size_hint=(0.12, 0.055),
                pos_hint={'right': 0.95, 'top': 0.88 - i * 0.07},
                color=(1, 1, 1, 1),
                font_size=14
            )
            btn.bind(on_press=callback)
            root.add_widget(btn)

        # Область таблицы
        self. scroll_view = ScrollView(
            size_hint=(0.7, 0.55),
            pos_hint={'x': 0.05, 'top': 0.78},
            do_scroll_x=True,
            do_scroll_y=True,
            bar_color=(0.4, 0.6, 0.9, 0.8),
            bar_width=8
        )

        self.grid = GridLayout(
            cols=1,
            spacing=2,
            size_hint=(None, None),
            padding=5
        )
        self.grid.bind(minimum_height=self. grid.setter('height'))
        self.grid.bind(minimum_width=self.grid.setter('width'))

        self.scroll_view.add_widget(self.grid)
        root.add_widget(self.scroll_view)

        self.init_table()

        send_btn = StyledButton(
            text="ОТПРАВИТЬ В KAFKA",
            bg_color=(0.2, 0.6, 0.9, 1),
            size_hint=(0.4, 0.08),
            pos_hint={'center_x':  0.4, 'y': 0.08},
            font_size=18,
            bold=True
        )
        send_btn.bind(on_press=self.send_to_kafka)
        root.add_widget(send_btn)

        self.status_label = Label(
            text="Готов к работе",
            font_size=14,
            color=(0.6, 0.8, 0.6, 1),
            size_hint=(0.5, 0.05),
            pos_hint={'center_x': 0.4, 'y': 0.02}
        )
        root.add_widget(self.status_label)

        return root

    def init_table(self):
        self.grid.clear_widgets()
        self.data_grid = []
        for _ in range(3):
            self.add_row(None)

    def create_cell(self, text=""):
        cell = TextInput(
            text=text,
            multiline=False,
            size_hint=(None, None),
            size=(120, 40),
            background_color=(0.22, 0.22, 0.28, 1),
            foreground_color=(0.95, 0.95, 0.95, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[10, 10]
        )
        return cell

    def add_row(self, instance):
        row_layout = GridLayout(cols=self.columns, spacing=2, size_hint=(None, None))
        row_layout.height = 40
        row_layout.width = self.columns * 122

        row_data = []
        for _ in range(self.columns):
            cell = self.create_cell()
            row_layout.add_widget(cell)
            row_data.append(cell)

        self.data_grid.append(row_data)
        self.grid.add_widget(row_layout)
        self.rows_count += 1
        self.update_status(f"Добавлена строка.  Всего:  {self.rows_count}")

    def add_column(self, instance):
        self.columns += 1
        for i, row_layout in enumerate(self.grid.children[: :-1]):
            cell = self.create_cell()
            row_layout.cols = self.columns
            row_layout.width = self.columns * 122
            row_layout.add_widget(cell)
            self.data_grid[i].append(cell)
        self.update_status(f"Добавлен столбец. Всего:  {self.columns}")

    def remove_row(self, instance):
        if self.rows_count > 1:
            self. grid.remove_widget(self.grid.children[0])
            self.data_grid.pop()
            self.rows_count -= 1
            self.update_status(f"Удалена строка. Всего: {self.rows_count}")

    def remove_column(self, instance):
        if self.columns > 1:
            self. columns -= 1
            for i, row_layout in enumerate(self. grid.children[::-1]):
                row_layout.remove_widget(row_layout.children[0])
                row_layout.cols = self.columns
                row_layout.width = self.columns * 122
                self.data_grid[i]. pop()
            self.update_status(f"Удален столбец. Всего:  {self.columns}")

    def clear_table(self, instance):
        self.columns = 3
        self.rows_count = 0
        self.table_name_input.text = ""
        self.init_table()
        self.update_status("Таблица очищена")

    def load_file(self, instance):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            try: 
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        data = json. load(f)
                        self.load_json_data(data)
                    elif file_path.endswith('.csv'):
                        self.load_csv_data(f)
                self.update_status(f"Файл загружен:  {file_path. split('/')[-1]}")
            except Exception as e:
                self.show_popup("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def load_json_data(self, data):
        if 'rows' in data:
            rows = data['rows']
            if rows:
                self.columns = len(rows[0])
                self.rows_count = 0
                self.grid.clear_widgets()
                self.data_grid = []
                for row in rows:
                    self.add_row(None)
                    for j, value in enumerate(row):
                        if j < len(self.data_grid[-1]):
                            self.data_grid[-1][j].text = str(value)

    def load_csv_data(self, file):
        import csv
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)
        if rows:
            self.columns = len(rows[0])
            self.rows_count = 0
            self.grid.clear_widgets()
            self.data_grid = []
            for row in rows:
                self.add_row(None)
                for j, value in enumerate(row):
                    if j < len(self.data_grid[-1]):
                        self.data_grid[-1][j].text = str(value)

    def send_to_kafka(self, instance):
        table_name = self.table_name_input.text.strip() or "unnamed_table"
        data = {
            "table_name": table_name,
            "columns": self.columns,
            "rows": []
        }

        for row in self.data_grid:
            row_values = [cell.text for cell in row]
            data["rows"].append(row_values)

        if not self.producer:
            try:
                with open('data_output.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.update_status(f"✓ Данные сохранены в data_output.json")
                self.show_popup("Успех", "Данные сохранены в файл data_output.json\n(Kafka недоступна)")
            except Exception as e:
                self.show_popup("Ошибка", f"Не удалось сохранить данные:\n{e}")
            return

        try:
            future = self.producer.send('data_topic', value=data)
            self.producer.flush()
            record_metadata = future.get(timeout=10)
            self.update_status(f"✓ Отправлено в топик: {record_metadata.topic}")
            self.show_popup("Успех", f"Данные отправлены в Kafka!\nТопик: {record_metadata.topic}")
        except KafkaError as e:
            self.show_popup("Ошибка Kafka", str(e))
            self.update_status("✗ Ошибка отправки")

    def update_status(self, text):
        if hasattr(self, 'status_label'):
            self.status_label.text = text

    def show_popup(self, title, message):
        content = FloatLayout()
        label = Label(
            text=message,
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5, 'top': 0.9},
            text_size=(280, None),
            halign='center'
        )
        close_btn = StyledButton(
            text="OK",
            bg_color=(0.3, 0.5, 0.8, 1),
            size_hint=(0.4, 0.2),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        content.add_widget(label)
        content.add_widget(close_btn)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.5, 0.4),
            background_color=(0.2, 0.2, 0.25, 1)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    KafkaDataSender().run()