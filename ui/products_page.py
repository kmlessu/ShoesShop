from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QScrollArea, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, Signal
import os


class ProductsPage(QWidget):

    back_requested = Signal()

    def __init__(self, role_name="Гость", products=None, full_name=None):
        super().__init__()

        self.role_name = str(role_name)
        self.full_name = full_name or role_name
        self.products = products or []

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

        self.back_btn = QPushButton("← Назад")
        self.back_btn.setFixedSize(130, 40)
        self.back_btn.setFont(QFont("Times New Roman", 18))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #7CFC00;
            }
        """)
        self.back_btn.clicked.connect(self.back_requested.emit)

        left_container = QWidget()
        left_container.setStyleSheet("background: white;")
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.back_btn)
        header_layout.addWidget(left_container)

        center_block = QWidget()
        center_block.setFixedHeight(60)
        center_block.setStyleSheet("background-color: #7FFF00")
        center_layout = QHBoxLayout(center_block)
        center_layout.setContentsMargins(20, 5, 20, 5)
        center_layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(f"Список товаров")
        self.title_label.setFont(QFont("Times New Roman", 26))
        self.title_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.title_label)

        header_layout.addWidget(center_block, stretch=1)

        right_container = QWidget()
        right_container.setStyleSheet("background: white;")
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        name_block = QWidget()
        name_block.setFixedHeight(65)
        name_block.setStyleSheet("background-color: #7FFF00")
        name_inner = QHBoxLayout(name_block)
        name_inner.setContentsMargins(20, 5, 20, 5)

        name_label = QLabel(str(self.full_name))
        name_label.setFont(QFont("Times New Roman", 26))
        name_inner.addWidget(name_label)
        right_layout.addWidget(name_block)

        logo_block = QWidget()
        logo_block.setFixedSize(65, 65)
        logo_block.setStyleSheet("background-color: white")
        logo_inner = QHBoxLayout(logo_block)
        logo_inner.setContentsMargins(5, 5, 5, 5)
        logo_inner.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        try:
            from PySide6.QtGui import QPixmap
            logo = QPixmap("resources/logo.png").scaled(58, 55, Qt.KeepAspectRatio)
            logo_label.setPixmap(logo)
        except:
            logo_label.setText("LOGO")
        logo_inner.addWidget(logo_label)

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
        scroll.setMinimumHeight(500)

        scroll.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #ccc;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: white;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(15)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setAlignment(Qt.AlignTop)

        self._add_products_to_layout(self.container_layout)

        scroll.setWidget(self.container)
        content_layout.addWidget(scroll)

        main_layout.addWidget(content_widget, stretch=1)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(main_container)

    def _add_products_to_layout(self, layout):
        try:
            from ui.product_item_widget import ProductItemWidget

            if not self.products:
                no_products_label = QLabel("Товары не найдены")
                no_products_label.setAlignment(Qt.AlignCenter)
                no_products_label.setFont(QFont("Times New Roman", 16))
                layout.addWidget(no_products_label)
                return

            for p in self.products:
                try:
                    item = ProductItemWidget(p)
                    item.setFixedHeight(210)
                    layout.addWidget(item)
                except Exception:
                    continue

        except Exception:
            no_products_label = QLabel("Ошибка загрузки товаров")
            no_products_label.setAlignment(Qt.AlignCenter)
            no_products_label.setFont(QFont("Times New Roman", 16))
            layout.addWidget(no_products_label)

    def update_products(self, new_products):
        self.products = new_products
        self.title_label.setText(f"Список товаров")

        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._add_products_to_layout(self.container_layout)