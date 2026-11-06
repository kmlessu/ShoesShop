from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, Signal


class OrderItemWidget(QWidget):

    clicked = Signal()

    def __init__(self):
        super().__init__()


        self.setCursor(QCursor(Qt.PointingHandCursor))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(0)

        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Box)
        self.card_frame.setLineWidth(2)
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid black;
            }
        """)

        frame_layout = QHBoxLayout(self.card_frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        frame_layout.setSpacing(20)

        main_layout.addWidget(self.card_frame)

        left_container = QWidget()
        left_container.setStyleSheet("background: transparent;")

        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        def make_label(text, bold=False, size=16):
            lbl = QLabel(text)
            lbl.setFont(QFont("Times New Roman", size, QFont.Bold if bold else QFont.Normal))
            lbl.setStyleSheet("border: none; background: transparent;")
            lbl.setWordWrap(True)
            return lbl

        self.lbl_code = make_label("Артикул", bold=True, size=18)
        self.lbl_status = make_label("Статус заказа", size=16)
        self.lbl_address = make_label("Адрес пункта выдачи", size=16)
        self.lbl_order_date = make_label("Дата заказа", size=16)

        left_layout.addWidget(self.lbl_code)
        left_layout.addWidget(self.lbl_status)
        left_layout.addWidget(self.lbl_address)
        left_layout.addWidget(self.lbl_order_date)

        frame_layout.addWidget(left_container, stretch=3)

        right_container = QFrame()
        right_container.setFrameShape(QFrame.Box)
        right_container.setLineWidth(1)
        right_container.setFixedSize(220, 130)
        right_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid black;
            }
        """)

        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignCenter)

        self.lbl_delivery_date = QLabel("Дата доставки")
        self.lbl_delivery_date.setFont(QFont("Times New Roman", 16))
        self.lbl_delivery_date.setAlignment(Qt.AlignCenter)
        self.lbl_delivery_date.setWordWrap(True)
        self.lbl_delivery_date.setStyleSheet("border: none; background: transparent;")

        right_layout.addWidget(self.lbl_delivery_date)

        frame_layout.addWidget(right_container)

        self.order_data = None
        self.order_id = None

        self.setStyleSheet("""
            OrderItemWidget:hover {
                background-color: #f5f5f5;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def set_order_data(self, order_data):
        self.order_data = order_data
        self.order_id = order_data.get("id")

        code = order_data.get("sku", order_data.get("pickup_code", ""))
        status = order_data.get("status", "")
        delivery_point = order_data.get("delivery_point", "")
        order_date = order_data.get("order_date", "")
        delivery_date = order_data.get("delivery_date", "")

        from datetime import datetime
        def fmt(date):
            try:
                return datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
            except:
                return date

        if order_date:
            order_date = fmt(order_date)
        if delivery_date:
            delivery_date = fmt(delivery_date)

        self.lbl_code.setText(f"Артикул: {code}")
        self.lbl_status.setText(f"Статус: {status}")
        self.lbl_address.setText(f"Адрес: {delivery_point}")
        self.lbl_order_date.setText(f"Дата заказа: {order_date}")
        self.lbl_delivery_date.setText(f"Дата доставки:\n{delivery_date}")

    def get_order_data(self):
        return self.order_data

    def get_order_id(self):
        return self.order_id