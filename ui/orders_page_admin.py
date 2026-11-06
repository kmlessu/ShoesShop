from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

from ui.order_item_widget import OrderItemWidget
from database import db


class OrdersPageAdmin(QWidget):

    def __init__(self, role_name="Администратор", go_back=None,
                 open_add_order=None, open_edit_order=None, full_name="Администратор"):
        super().__init__()

        self.go_back = go_back
        self.open_add_order = open_add_order
        self.open_edit_order = open_edit_order
        self.role_name = role_name
        self.full_name = full_name

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
        back_btn.clicked.connect(self.go_back)

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

        self.title_label = QLabel("Список заказов")
        self.title_label.setFont(QFont("Times New Roman", 26))
        self.title_label.setStyleSheet("background-color: transparent;")
        self.title_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.title_label)

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
            logo = QPixmap("resources/logo.png").scaled(58, 55, Qt.KeepAspectRatio)
            logo_label.setPixmap(logo)
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

        self.btn_add = QPushButton("Добавить заказ")
        self.btn_add.setFixedHeight(40)
        self.btn_add.setFont(QFont("Times New Roman", 20))
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #7CFC00;
            }
        """)
        self.btn_add.clicked.connect(self._add_order)
        content_layout.addWidget(self.btn_add)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: white;")
        self.cl = QVBoxLayout(self.container)
        self.cl.setAlignment(Qt.AlignTop)
        self.cl.setSpacing(15)
        self.cl.setContentsMargins(10, 10, 10, 10)

        self.scroll.setWidget(self.container)
        content_layout.addWidget(self.scroll)

        self.order_widgets = []

        main_layout.addWidget(content_widget, stretch=1)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(main_container)

        self._load_orders_list()

    def _add_order(self):
        if self.open_add_order:
            self.open_add_order()

    def _load_orders_list(self):
        self._safe_clear_container()

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
                    order_id = order.get('id')
                    sku_string = order.get('sku_string', "")

                    item = OrderItemWidget()
                    item.setFixedHeight(180)

                    display_data = {
                        "id": order_id,
                        "sku": sku_string,
                        "status": order.get("status", "Неизвестно"),
                        "delivery_point": order.get("delivery_point", "Не указан"),
                        "order_date": order.get("order_date", ""),
                        "delivery_date": order.get("delivery_date", "")
                    }

                    item.set_order_data(display_data)

                    item.clicked.connect(lambda checked=False, oid=order_id: self._on_order_click(oid))

                    self.cl.addWidget(item)
                    self.order_widgets.append(item)

                except Exception:
                    continue

            self.title_label.setText(f"Список заказов")

        except Exception as e:
            error_label = QLabel(f"Ошибка загрузки заказов: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setFont(QFont("Times New Roman", 14))
            error_label.setStyleSheet("background-color: white;")
            self.cl.addWidget(error_label)

    def _safe_clear_container(self):
        while self.cl.count():
            item = self.cl.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                try:
                    widget.clicked.disconnect()
                except:
                    pass
                widget.setParent(None)
                if hasattr(widget, 'deleteLater'):
                    widget.deleteLater()

        self.order_widgets.clear()

    def _on_order_click(self, order_id):
        if self.open_edit_order and order_id:
            try:
                self.open_edit_order(order_id)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть заказ для редактирования: {str(e)}")

    def refresh_orders(self):
        self._safe_clear_container()
        self._load_orders_list()

    def cleanup(self):
        self._safe_clear_container()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_orders_list()