import sys
import json
import win32print  # Windows yazıcı modülü
import win32ui
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox

ORDERS_FILE = "orders.json"

class PaymentSystem(QWidget):
    def __init__(self,main_menu=None):
        super().__init__()
        self.main_menu = main_menu 

        self.setWindowTitle("Ödeme & Fiş Yazdırma")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.label_orders = QLabel("Fiş İçeriği:")
        layout.addWidget(self.label_orders)

        self.order_list = QListWidget()
        layout.addWidget(self.order_list)

        self.total_label = QLabel("Toplam: 0.00 TL")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
        layout.addWidget(self.total_label)

        self.complete_button = QPushButton("Ödemeyi Tamamla")
        self.complete_button.setStyleSheet("font-size: 25px; background-color: green; color: white;")  # **Ödeme butonu büyütüldü ve yeşil yapıldı**
        self.complete_button.clicked.connect(self.complete_payment)
        layout.addWidget(self.complete_button)

        self.print_button = QPushButton("Fişi Yazdır")
        self.print_button.setStyleSheet("font-size: 18px;")  # **Ödeme butonu büyütüldü ve yeşil yapıldı**
        self.print_button.clicked.connect(self.print_receipt)
        layout.addWidget(self.print_button)

        self.setLayout(layout)
        self.load_orders()

    def load_orders(self):
        """Siparişleri `orders.json` dosyasından yükler."""
        try:
            with open(ORDERS_FILE, "r") as f:
                orders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            orders = []

        self.order_list.clear()
        total_price = sum(price for _, _, price in orders)
        self.total_label.setText(f"Toplam: {total_price:.2f} TL")

        for drink, size, price in orders:
            self.order_list.addItem(f"{drink} ({size} oz) - {price:.2f} TL")

    def print_receipt(self):
        """Windows yazıcısından fiş çıkarır."""
        try:
            printer_name = win32print.GetDefaultPrinter()  # Varsayılan yazıcıyı al

            receipt_text = "\n".join(self.order_list.item(i).text() for i in range(self.order_list.count()))
            receipt_text += f"\n-------------------------\nToplam: {self.total_label.text()}\n\nTeşekkürler!"

            hprinter = win32print.OpenPrinter(printer_name)
            printer_info = win32print.GetPrinter(hprinter, 2)
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(printer_name)
            pdc.StartDoc('Fiş Yazdırma')
            pdc.StartPage()
            pdc.TextOut(100, 100, receipt_text)
            pdc.EndPage()
            pdc.EndDoc()
            pdc.DeleteDC()

            QMessageBox.information(self, "Başarılı", "Fiş yazdırıldı!")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Fiş yazdırma başarısız: {e}")

    def complete_payment(self):
        """Ödemeyi tamamlar ve siparişleri temizler."""
        with open(ORDERS_FILE, "w") as f:
            json.dump([], f)

        self.load_orders()
        #QMessageBox.information(self, "Ödeme Tamamlandı", "Sipariş sıfırlandı ve ödeme alındı!")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentSystem()
    window.show()
    sys.exit(app.exec())
