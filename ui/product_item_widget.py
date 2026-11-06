from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont, QPixmap, QCursor, QPainter, QPen
from PySide6.QtCore import Qt, Signal
import os


class ProductItemWidget(QWidget):
    clicked = Signal()

    def __init__(self, product=None):
        super().__init__()

        self.product = product or {}
        self.sku = self.product.get("sku")

        self.discount = self.product.get("discount", 0)
        self.has_discount = self.discount > 0
        self.has_high_discount = self.discount > 15
        self.quantity = self.product.get("quantity", 0)
        self.is_out_of_stock = self.quantity == 0

        self.setCursor(QCursor(Qt.PointingHandCursor))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(0)

        card = QWidget()
        card.setObjectName("card_frame")

        card_style = "background: white;"
        if self.has_high_discount:
            card_style = "background: #2E8B57;"
        elif self.is_out_of_stock:
            card_style = "background: #ADD8E6;"

        card.setStyleSheet(f"QWidget#card_frame {{ {card_style} border: 2px solid black; }}")

        main_layout.addWidget(card)

        inner_lay = QHBoxLayout(card)
        inner_lay.setContentsMargins(10, 10, 30, 10)
        inner_lay.setSpacing(20)

        photo_container = QWidget()
        photo_container.setObjectName("photo_container")
        photo_container.setFixedSize(230, 160)

        ph = QVBoxLayout(photo_container)
        ph.setContentsMargins(0, 0, 0, 0)

        photo_label = QLabel()
        photo_label.setAlignment(Qt.AlignCenter)

        photo_path = self.product.get("photo_filename")
        pix = None

        if photo_path and os.path.exists(photo_path):
            pix = QPixmap(photo_path)
        elif os.path.exists("resources/picture.png"):
            pix = QPixmap("resources/picture.png")

        if pix and not pix.isNull():
            photo_label.setPixmap(
                pix.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            photo_label.setText("Фото")
            photo_label.setFont(QFont("Times New Roman", 16))

        ph.addWidget(photo_label)
        inner_lay.addWidget(photo_container)

        center = QWidget()
        center.setObjectName("center_block")

        center_lay = QVBoxLayout(center)
        center_lay.setSpacing(5)
        center_lay.setContentsMargins(0, 0, 0, 0)

        title = QLabel(
            f"{self.product.get('category', '')} | {self.product.get('name', '')}"
        )
        title.setFont(QFont("Times New Roman", 17, QFont.Bold))

        if self.is_out_of_stock:
            title.setText(f"{self.product.get('category', '')} | {self.product.get('name', '')} [НЕТ В НАЛИЧИИ]")

        center_lay.addWidget(title)

        def create_info_label(label, value):
            lbl = QLabel(f"{label}: {value}")
            lbl.setFont(QFont("Times New Roman", 14))
            return lbl

        center_lay.addWidget(create_info_label("Описание товара", self.product.get("description", "")))

        center_lay.addWidget(create_info_label("Производитель", self.product.get("manufacturer", "")))

        center_lay.addWidget(create_info_label("Поставщик", self.product.get("supplier", "")))

        price_row = QHBoxLayout()
        price_row.setContentsMargins(0, 0, 0, 0)
        price_row.setSpacing(10)

        price = self.product.get("price", 0)

        def format_price(value):
            price_str = f"{value:.2f}"
            return price_str.replace('.', ',')

        if self.has_discount:
            discounted_price = price * (100 - self.discount) / 100

            original_price_formatted = format_price(price)
            discounted_price_formatted = format_price(discounted_price)

            original_price_label = QLabel(f"{original_price_formatted} руб.")
            original_price_label.setFont(QFont("Times New Roman", 14))
            original_price_label.setStyleSheet("color: red; text-decoration: line-through;")

            arrow_label = QLabel("→")
            arrow_label.setFont(QFont("Times New Roman", 14))
            arrow_label.setStyleSheet("color: black;")

            discounted_price_label = QLabel(f"{discounted_price_formatted} руб.")
            discounted_price_label.setFont(QFont("Times New Roman", 14))
            discounted_price_label.setStyleSheet("color: black; font-weight: bold;")

            price_row.addWidget(original_price_label)
            price_row.addWidget(arrow_label)
            price_row.addWidget(discounted_price_label)
            price_row.addStretch()
        else:
            price_formatted = format_price(price)
            price_label = QLabel(f"Цена: {price_formatted} руб.")
            price_label.setFont(QFont("Times New Roman", 14))
            price_label.setStyleSheet("color: black;")
            price_row.addWidget(price_label)

        center_lay.addLayout(price_row)

        center_lay.addWidget(create_info_label("Единица измерения", self.product.get("unit", "")))

        quantity_label = create_info_label("Количество на складе", self.product.get("quantity", ""))
        if self.is_out_of_stock:
            quantity_label.setStyleSheet("color: black; font-weight: bold;")
        center_lay.addWidget(quantity_label)

        inner_lay.addWidget(center, stretch=2)

        right = QWidget()
        right.setObjectName("right_block")
        right.setFixedSize(140, 150)

        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setAlignment(Qt.AlignCenter)

        disc_label = QLabel("Действующая\nскидка")
        disc_label.setFont(QFont("Times New Roman", 15))
        disc_label.setAlignment(Qt.AlignCenter)
        rl.addWidget(disc_label)

        disc_value = QLabel(f"{self.discount}%")
        disc_value.setFont(QFont("Times New Roman", 24, QFont.Bold))
        disc_value.setAlignment(Qt.AlignCenter)
        rl.addWidget(disc_value)

        inner_lay.addWidget(right)

        container_styles = f"""
            QWidget#photo_container {{
                border: 1px solid black;
                background: white;
            }}
            QWidget#right_block {{
                border: 1px solid black;
                background: transparent;
            }}
            QWidget#center_block {{
                background: transparent;
            }}
            ProductItemWidget:hover {{
                background-color: #f5f5f5;
            }}
            QLabel {{
                background: transparent;
            }}
        """

        self.setStyleSheet(container_styles)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()