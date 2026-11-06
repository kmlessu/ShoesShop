from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QListView, QMessageBox,
    QScrollArea, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.product_item_widget import ProductItemWidget
from database import db


class FixedComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        view = QListView()
        view.setMinimumHeight(70)
        self.setView(view)

    def showPopup(self):
        self.view().setMinimumWidth(self.width() + 40)
        super().showPopup()


class ManagerPage(QWidget):

    back_to_login = Signal()

    def __init__(self, full_name="", go_back=None, open_orders=None):
        super().__init__()

        self.full_name = full_name
        self.go_back = go_back
        self.open_orders = open_orders

        self.products = db.get_all_products()
        self.filtered_products = self.products.copy()

        self.current_search_text = ""
        self.current_supplier = "Все поставщики"
        self.current_sort_mode = "Сортировка ↑"

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
        back_btn.clicked.connect(self._on_back_to_login)

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

        self.title_label = QLabel("Список товаров")
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
            from PySide6.QtGui import QPixmap
            logo = QPixmap("resources/logo.png").scaled(58, 55, Qt.KeepAspectRatio)
            logo_label.setPixmap(logo)
        except:
            pass
        logo_inner_layout.addWidget(logo_label)

        right_layout.addWidget(logo_block)
        header_layout.addWidget(right_container)

        main_layout.addWidget(header_widget)

        tools_widget = QWidget()
        tools_widget.setStyleSheet("background-color: white;")
        tools_widget.setFixedHeight(60)

        tools_layout = QHBoxLayout(tools_widget)
        tools_layout.setContentsMargins(20, 10, 20, 10)
        tools_layout.setSpacing(15)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск…")
        self.search_field.setFixedWidth(550)
        self.search_field.setFixedHeight(34)
        self.search_field.setText(self.current_search_text)
        self.search_field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid black;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 14px;
                background-color: white;
            }
        """)
        tools_layout.addWidget(self.search_field)

        self.filter_supplier = FixedComboBox()
        self.filter_supplier.addItem("Все поставщики")
        self.filter_supplier.setFixedWidth(200)
        self.filter_supplier.setFixedHeight(34)
        self.filter_supplier.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid black;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 14px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox QAbstractItemView {
                border-radius: 8px;
                background-color: white;
                selection-background-color: #7FFF00;
                selection-color: black;
            }
        """)

        suppliers = sorted(set(p.get("supplier", "") for p in self.products if p.get("supplier")))
        for s in suppliers:
            self.filter_supplier.addItem(s)

        index = self.filter_supplier.findText(self.current_supplier)
        if index >= 0:
            self.filter_supplier.setCurrentIndex(index)

        tools_layout.addWidget(self.filter_supplier)

        self.sort_combo = FixedComboBox()
        self.sort_combo.addItems(["Сортировка ↑", "Сортировка ↓"])
        self.sort_combo.setFixedWidth(200)
        self.sort_combo.setFixedHeight(34)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid black;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 14px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox QAbstractItemView {
                border-radius: 8px;
                background-color: white;
                selection-background-color: #7FFF00;
                selection-color: black;
            }
        """)

        index = self.sort_combo.findText(self.current_sort_mode)
        if index >= 0:
            self.sort_combo.setCurrentIndex(index)

        tools_layout.addWidget(self.sort_combo)

        btn_orders = QPushButton("Заказы")
        btn_orders.setFixedSize(130, 34)
        btn_orders.setFont(QFont("Times New Roman", 18))
        btn_orders.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #7CFC00;
            }
        """)
        btn_orders.clicked.connect(self._open_orders)
        tools_layout.addWidget(btn_orders)

        tools_layout.addStretch()

        main_layout.addWidget(tools_widget)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 10, 20, 20)
        content_layout.setSpacing(10)

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

        self.search_field.textChanged.connect(self._on_search_changed)
        self.filter_supplier.currentTextChanged.connect(self._on_supplier_changed)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)

    def _on_back_to_login(self):
        self.back_to_login.emit()

        if self.go_back:
            self.go_back()

    def _on_search_changed(self, text):
        self.current_search_text = text
        self.apply_filters()

    def _on_supplier_changed(self, supplier):
        self.current_supplier = supplier
        self.apply_filters()

    def _on_sort_changed(self, sort_mode):
        self.current_sort_mode = sort_mode
        self.apply_filters()

    def apply_filters(self):
        text = self.current_search_text.lower().strip()
        supplier = self.current_supplier
        sort_mode = self.current_sort_mode

        result = self.products.copy()
        if supplier != "Все поставщики":
            result = [p for p in result if p.get("supplier") == supplier]

        if text:
            def matches(p):
                name = str(p.get("name", "")).lower()
                description = str(p.get("description", "")).lower()
                manufacturer = str(p.get("manufacturer", "")).lower()
                supplier_text = str(p.get("supplier", "")).lower()
                category = str(p.get("category", "")).lower()
                sku = str(p.get("sku", "")).lower()

                search_words = text.split()

                for search_word in search_words:
                    if (search_word in name or
                            search_word in description or
                            search_word in manufacturer or
                            search_word in supplier_text or
                            search_word in category or
                            search_word in sku):
                        continue
                    else:
                        return False

                return True

            result = [p for p in result if matches(p)]

        reverse = (sort_mode == "Сортировка ↓")
        result.sort(key=lambda p: p.get("quantity", 0), reverse=reverse)

        self.filtered_products = result
        self._update_products_display()

    def _update_products_display(self):
        if not hasattr(self, 'container_layout'):
            return

        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

        self._add_products_to_layout(self.container_layout)

    def _add_products_to_layout(self, layout):
        if not self.filtered_products:
            no_products_label = QLabel("Товары не найдены")
            no_products_label.setAlignment(Qt.AlignCenter)
            no_products_label.setFont(QFont("Times New Roman", 16))
            no_products_label.setStyleSheet("background-color: white;")
            layout.addWidget(no_products_label)
            return

        for product in self.filtered_products:
            try:
                item = ProductItemWidget(product)
                item.setFixedHeight(210)
                layout.addWidget(item)
            except Exception:
                continue

    def _open_orders(self):
        if self.open_orders:
            self.open_orders()

    def refresh_products(self):
        self.products = db.get_all_products()
        self.apply_filters()

    def update_products(self, new_products):
        self.products = new_products
        self.apply_filters()

    def refresh(self):
        self.refresh_products()