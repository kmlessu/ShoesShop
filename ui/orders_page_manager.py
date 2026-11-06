from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

from ui.order_item_widget import OrderItemWidget
from database import db


class OrdersPageManager(QWidget):

    def __init__(self, role_name="Менеджер", go_back=None, full_name="Менеджер"):
        super().__init__()

        self.role_name = role_name
        self.full_name = full_name
        self.go_back = go_back

        main_container = QWidget()
        main_container.setStyleSheet("background-color: #FFFFFF;")

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setStyleSheet("background: white;")
        header_widget.setFixedHeight(80)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(20)

        back_btn = QPushButton("← Назад")
        back_btn.setFixedSize(130, 40)
        back_btn.setFont(QFont("Times New Roman", 20))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #7CFC00;
            }
        """)
        back_btn.clicked.connect(self._go_back)

        left_container = QWidget()
        left_container.setStyleSheet("background: white;")
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(back_btn)
        header_layout.addWidget(left_container)

        center_block = QWidget()
        center_block.setFixedHeight(60)
        center_block.setStyleSheet("""
            background-color: #7FFF00
        """)
        center_layout = QHBoxLayout(center_block)
        center_layout.setContentsMargins(20, 5, 20, 5)

        title_label = QLabel("Список заказов")
        title_label.setFont(QFont("Times New Roman", 26))
        title_label.setStyleSheet("background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(title_label)

        header_layout.addWidget(center_block, stretch=1)

        right_container = QWidget()
        right_container.setStyleSheet("background: white;")
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        role_block = QWidget()
        role_block.setFixedHeight(65)
        role_block.setStyleSheet("""
            background-color: #7FFF00
        """)
        role_inner_layout = QHBoxLayout(role_block)
        role_inner_layout.setContentsMargins(20, 5, 20, 5)

        role_label = QLabel(self.full_name)
        role_label.setStyleSheet("background-color: transparent;")
        role_label.setFont(QFont("Times New Roman", 26))

        role_inner_layout.addWidget(role_label)

        right_layout.addWidget(role_block)

        logo_block = QWidget()
        logo_block.setFixedSize(65, 65)
        logo_block.setStyleSheet("""
            background-color: white
        """)
        logo_inner_layout = QHBoxLayout(logo_block)
        logo_inner_layout.setContentsMargins(5, 5, 5, 5)
        logo_inner_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        try:
            pixmap = QPixmap("resources/logo.png").scaled(58, 55, Qt.KeepAspectRatio)
            logo_label.setPixmap(pixmap)
        except:
            pass
        logo_inner_layout.addWidget(logo_label)

        right_layout.addWidget(logo_block)
        header_layout.addWidget(right_container)

        main_layout.addWidget(header_widget)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: white;")
        self.cl = QVBoxLayout(self.container)
        self.cl.setContentsMargins(10, 10, 10, 10)
        self.cl.setSpacing(20)
        self.cl.setAlignment(Qt.AlignTop)

        self._load_orders()

        scroll.setWidget(self.container)
        content_layout.addWidget(scroll)

        main_layout.addWidget(content_widget, stretch=1)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(main_container)

    def _get_order_sku_string(self, order_id):
        try:
            return db.get_order_sku_string(order_id)
        except Exception as e:
            print(f"❌ Ошибка получения артикулов заказа {order_id}: {e}")
            return ""

    def _load_orders(self):
        try:
            orders = db.get_all_orders()

            if not orders:
                no_orders_label = QLabel("Заказов нет")
                no_orders_label.setAlignment(Qt.AlignCenter)
                no_orders_label.setFont(QFont("Times New Roman", 16))
                no_orders_label.setStyleSheet("background-color: white;")
                self.cl.addWidget(no_orders_label)
                return

            for order in orders:
                try:
                    item = OrderItemWidget()

                    order_id = order.get("id")
                    sku_string = self._get_order_sku_string(order_id)

                    display_data = {
                        "id": order_id,
                        "sku": sku_string,
                        "status": order.get("status", "Неизвестно"),
                        "delivery_point": order.get("delivery_point", "Не указан"),
                        "order_date": order.get("order_date", ""),
                        "delivery_date": order.get("delivery_date", "")
                    }

                    item.set_order_data(display_data)
                    self.cl.addWidget(item)

                except Exception as e:
                    print(f"Ошибка при добавлении заказа {order.get('id', 'unknown')}: {e}")
                    continue

        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")
            error_label = QLabel(f"Ошибка загрузки заказов: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setFont(QFont("Times New Roman", 14))
            error_label.setStyleSheet("background-color: white;")
            self.cl.addWidget(error_label)

    def _go_back(self):
        if self.go_back:
            self.go_back()

    def refresh_orders(self):
        print("\n🔄 Обновление списка заказов в OrdersPageManager...")

        while self.cl.count():
            item = self.cl.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

        self._load_orders()
        print("✅ Список заказов обновлен")