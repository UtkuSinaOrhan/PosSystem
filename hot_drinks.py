import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QMessageBox, QGridLayout
)
from functools import partial

ORDERS_FILE = "orders.json"

# Read and process the menu from file
fileName = "menu/hotDrinks.txt"
with open(fileName, 'r') as file:
    menu = [line.strip().split(',') for line in file]

for i in range(len(menu)):
    menu[i][0] = menu[i][0].lower()
    menu[i][1] = int(menu[i][1])
    menu[i][2] = float(menu[i][2])

drink_dict = {}
for item in menu:
    drink_dict.setdefault(item[0].capitalize(), []).append((item[1], item[2]))


class HotDrinks(QWidget):
    def __init__(self, main_menu=None):
        super().__init__()
        self.main_menu = main_menu  

        self.setWindowTitle("Sıcak İçecekler")
        self.setGeometry(100, 100, 600, 500)

        main_layout = QVBoxLayout()

        self.label_drink = QLabel("Bir içecek seçin:")
        main_layout.addWidget(self.label_drink)

        self.drink_grid = QGridLayout()
        row, col = 0, 0
        for drink in drink_dict.keys():
            btn = QPushButton(drink)
            btn.setFixedSize(200, 60)
            btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: white; color: black;")
            btn.clicked.connect(partial(self.select_drink, drink))
            self.drink_grid.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        main_layout.addLayout(self.drink_grid)

        self.label_size = QLabel("")
        self.label_size.hide()
        main_layout.addWidget(self.label_size)

        self.size_buttons_layout = QHBoxLayout()
        self.size_buttons = []
        main_layout.addLayout(self.size_buttons_layout)

        self.label_orders = QLabel("Siparişler:")
        main_layout.addWidget(self.label_orders)

        self.order_list = QListWidget()
        main_layout.addWidget(self.order_list)

        self.total_label = QLabel("Toplam: 0.00 TL")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
        main_layout.addWidget(self.total_label)

        bottom_buttons = QHBoxLayout()
        self.delete_button = QPushButton("Seçili Ürünü Sil")
        self.delete_button.setStyleSheet("font-size: 16px; background-color: white; color: red")  # **Silme butonu büyütüldü**
        self.delete_button.clicked.connect(self.delete_selected_order)
        bottom_buttons.addWidget(self.delete_button)

        self.clear_button = QPushButton("Siparişleri Temizle")
        self.clear_button.setStyleSheet("font-size: 16px; background-color: red; color: white")  # **Silme butonu büyütüldü**
        self.clear_button.clicked.connect(self.clear_orders)
        bottom_buttons.addWidget(self.clear_button)

        self.confirm_button = QPushButton("Siparişi Onayla")
        self.confirm_button.setStyleSheet("font-size: 16px; background-color: green; color: white;")  # **Ödeme butonu büyütüldü ve yeşil yapıldı**
        self.confirm_button.clicked.connect(self.confirm_order)
        bottom_buttons.addWidget(self.confirm_button)

        main_layout.addLayout(bottom_buttons)

        self.setLayout(main_layout)

        self.load_orders()

    def select_drink(self, drink):
        self.selected_drink = drink
        self.label_size.setText(f"{drink} için boyut seçin:")
        self.label_size.show()

        for btn in self.size_buttons:
            self.size_buttons_layout.removeWidget(btn)
            btn.deleteLater()
        self.size_buttons.clear()

        for size, price in drink_dict[drink]:
            btn = QPushButton(f"{size} oz")
            btn.setStyleSheet("font-size: 14px; font-weight: bold;")
            btn.setFixedSize(100, 50)
            btn.clicked.connect(partial(self.add_order, size, price))
            self.size_buttons.append(btn)
            self.size_buttons_layout.addWidget(btn)

    def add_order(self, size, price):
        if not self.selected_drink:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir içecek seçin.")
            return

        try:
            with open(ORDERS_FILE, "r") as f:
                orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            orders = []

        orders.append((self.selected_drink, size, price))

        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f)

        self.order_list.addItem(f"{self.selected_drink} ({size} oz) - {price:.2f} TL")
        self.load_orders()

    def load_orders(self):
        """Güncellenmiş siparişleri göster"""
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            orders = []
    
        self.order_list.clear()

        if not orders:
            no_orders_item = "Henüz sipariş eklenmedi!"
            self.order_list.addItem(no_orders_item)
            self.order_list.setStyleSheet("font-size: 16px; font-style: italic; color: gray;")  # **Sipariş yoksa büyüt & gri renkte göster**
        else:
            self.order_list.setStyleSheet("font-size: 18px;")  # **Siparişler varsa 18px büyüklüğünde göster**

        total_price = sum(price for _, _, price in orders)
        self.total_label.setText(f"Toplam: {total_price:.2f} TL")
        self.total_label.setStyleSheet("font-size: 22px; font-weight: bold; color: red;")  # **Toplam fiyat büyük ve kırmızı yapıldı**

        for drink, size, price in orders:
            self.order_list.addItem(f"{drink} ({size} oz) - {price:.2f} TL")


    def delete_selected_order(self):
        """Seçili ürünü sipariş listesinden ve orders.json'dan kaldırır"""
        selected_item = self.order_list.currentRow()
        if selected_item == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir ürün seçin.")
            return

        try:
            with open(ORDERS_FILE, "r") as f:
                orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            orders = []

        del orders[selected_item]

        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f)

        self.load_orders()
        if self.main_menu:
            self.main_menu.load_orders()  # Ana menüyü güncelle

    def clear_orders(self):
        with open(ORDERS_FILE, "w") as f:
            json.dump([], f)
        self.load_orders()

    def confirm_order(self):
        """Sipariş onaylandığında ana menü güncellenecek"""
        if self.main_menu:
            self.main_menu.load_orders()
        #QMessageBox.information(self, "Sipariş Onaylandı", "Siparişiniz güncellendi.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HotDrinks()
    window.show()
    sys.exit(app.exec())
