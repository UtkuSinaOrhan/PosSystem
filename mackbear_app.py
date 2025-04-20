import sys
import subprocess
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QListWidget, QMessageBox, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

ORDERS_FILE = "orders.json"
RECEIPT_FILE = "receipt_counter.json"  # **Fiş sayacı dosyası**

PAGES = {
    "Sıcak İçecekler": "hot_drinks.py",
    "Soğuk İçecekler": "cold_drinks.py",
    "Ekstralar": "extras.py",
    "Tatlılar": "desserts.py",
    "Sandviçler": "sandwiches.py",
    "Dolap İçecekleri": "fridge_drinks.py",
    "Kampanyalar": "campaigns.py",
    "Market": "market.py",
    "Mackbear Shop": "shop.py"
}

class MainMenu(QWidget):
    update_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mackbear Kasa Uygulaması")
        self.setGeometry(100, 100, 600, 500)

        main_layout = QVBoxLayout()

        # **Fiş Sayacı (En Üste)**
        self.receipt_count = 0  # **Fiş sayısını sıfırdan başlat**
        self.receipt_label = QLabel(f"Toplam Kesilen Fiş: {self.receipt_count}")
        self.receipt_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        main_layout.addWidget(self.receipt_label)

        # **Butonları GridLayout ile sıralıyoruz**
        grid_layout = QGridLayout()
        row, col = 0, 0
        max_columns = 3

        for label, filename in PAGES.items():
            btn = QPushButton(label)
            btn.setFixedSize(200, 60)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px; font-weight: bold; background-color: white; color: black; 
                    border: 2px solid black; border-radius: 10px;
                }
                QPushButton:hover { background-color: #f0f0f0; }
            """)
            btn.clicked.connect(lambda checked, f=filename: self.open_page(f))
            grid_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_columns:  
                col = 0
                row += 1

        main_layout.addLayout(grid_layout)

        # **Sipariş Listesi**
        self.label_orders = QLabel("Seçilen Ürünler:")
        self.label_orders.setStyleSheet("font-size: 18px; font-weight: bold")
        main_layout.addWidget(self.label_orders)

        self.order_list = QListWidget()
        self.order_list.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.order_list)

        self.total_label = QLabel("Toplam: 0.00 TL")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
        main_layout.addWidget(self.total_label)

        # **Alt Butonlar (Silme & Ödeme)**
        bottom_buttons = QHBoxLayout()

        self.delete_button = QPushButton("Seçili Ürünü Sil")
        self.delete_button.setStyleSheet("font-size: 16px;")
        self.delete_button.clicked.connect(self.delete_selected_order)
        bottom_buttons.addWidget(self.delete_button)

        self.complete_button = QPushButton("Siparişi Tamamla")
        self.complete_button.setStyleSheet("font-size: 16px; background-color: green; color: white;")
        self.complete_button.clicked.connect(self.complete_payment)
        bottom_buttons.addWidget(self.complete_button)

        main_layout.addLayout(bottom_buttons)

        self.setLayout(main_layout)

        self.update_signal.connect(self.load_orders)
        self.load_orders()

    def open_page(self, filename):
        if filename == "hot_drinks.py":
            from hot_drinks import HotDrinks
            self.drink_window = HotDrinks(main_menu=self)
            self.drink_window.show()
        elif filename == "payments.py":
            from payments import PaymentSystem
            self.payment_window = PaymentSystem(main_menu=self)
            self.payment_window.show()
        else:
            subprocess.Popen(["python", filename])

    def load_orders(self):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            orders = []

        self.order_list.clear()

        if not orders:
            self.order_list.addItem("Henüz sipariş eklenmedi!")
            self.order_list.setStyleSheet("font-size: 16px; font-style: italic; color: gray;")
        else:
            self.order_list.setStyleSheet("font-size: 18px;")

        total_price = sum(price for _, _, price in orders)
        self.total_label.setText(f"Toplam: {total_price:.2f} TL")
        self.total_label.setStyleSheet("font-size: 22px; font-weight: bold; color: red;")

        for drink, size, price in orders:
            self.order_list.addItem(f"{drink} ({size} oz) - {price:.2f} TL")

    def delete_selected_order(self):
        selected_item = self.order_list.currentRow()
        if selected_item == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir ürün seçin!")
            return

        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            orders = []

        del orders[selected_item]

        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f)

        self.load_orders()

    def complete_payment(self):
        """Siparişi tamamla, ödeme al ve fişi artır"""
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            orders = []

        if not orders:  # **Sipariş listesi boşsa işlem yapılmayacak**
            QMessageBox.warning(self, "Uyarı", "Boş sipariş veremezsiniz!")
            return

        from payments import PaymentSystem
        self.payment_window = PaymentSystem(main_menu=self)
        self.payment_window.show()

        # **Fiş sayacını artır**
        self.receipt_count += 1
        self.receipt_label.setText(f"Toplam Kesilen Fiş: {self.receipt_count}")

        # **Siparişleri sıfırla**
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

        self.load_orders()

    def closeEvent(self, event):
        """Uygulama kapanınca fiş sayacını sıfırla"""
        self.receipt_count = 0
        self.receipt_label.setText(f"Toplam Kesilen Fiş: {self.receipt_count}")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())
