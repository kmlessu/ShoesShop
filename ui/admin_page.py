from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QListView, QMessageBox, QLabel,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.product_item_widget import ProductItemWidget


class FixedComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        view = QListView()
        view.setMinimumHeight(70)
        self.setView(view)

    def showPopup(self):
        self.view().setMinimumWidth(self.width() + 40)
        super().showPopup()


class AdminPage(QWidget):
    need_refresh = Signal()
    back_to_login = Signal()

    def __init__(
            self,
            full_name="Администратор",
            go_back=None,
            open_orders=None,
            open_add_product=None,
            open_edit_product=None,
            products=None
    ):
        super().__init__()

        self.full_name = full_name
        self.go_back = go_back
        self.open_orders = open_orders
        self.open_add_product = open_add_product
        self.open_edit_product = open_edit_product

        self.products = products or []
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
        self.back_btn.clicked.connect(self._on_back_to_login)

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

        tools_widget = QWidget()
        tools_widget.setStyleSheet("background-color: white;")
        tools_widget.setFixedHeight(60)

        tools_layout = QHBoxLayout(tools_widget)
        tools_layout.setContentsMargins(20, 10, 20, 10)
        tools_layout.setSpacing(15)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск…")
        self.search_field.setFixedWidth(450)
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
        self.filter_supplier.setFixedWidth(180)
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

        idx = self.filter_supplier.findText(self.current_supplier)
        if idx >= 0:
            self.filter_supplier.setCurrentIndex(idx)

        tools_layout.addWidget(self.filter_supplier)

        self.sort_combo = FixedComboBox()
        self.sort_combo.addItems(["Сортировка ↑", "Сортировка ↓"])
        self.sort_combo.setFixedWidth(180)
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

        idx = self.sort_combo.findText(self.current_sort_mode)
        if idx >= 0:
            self.sort_combo.setCurrentIndex(idx)

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

        btn_add = QPushButton("Добавить товар")
        btn_add.setFixedSize(140, 34)
        btn_add.setFont(QFont("Times New Roman", 18))
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #7CFC00;
            }
        """)
        btn_add.clicked.connect(self._add_product)
        tools_layout.addWidget(btn_add)

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

        self.product_widgets = []

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

    def _widget_alive(self, w):
        if w is None:
            return False
        try:
            _ = w.metaObject()
            return True
        except RuntimeError:
            return False
        except Exception:
            return False

    def _on_back_to_login(self):
        try:
            self.back_to_login.emit()
        except Exception:
            pass

        if callable(self.go_back):
            try:
                self.go_back()
            except Exception:
                pass

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
        text = (self.current_search_text or "").lower().strip()
        supplier = self.current_supplier
        sort_mode = self.current_sort_mode

        result = list(self.products)

        if supplier and supplier != "Все поставщики":
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
        if not self._widget_alive(self.container):
            return

        for widget in self.product_widgets:
            try:
                if self._widget_alive(widget):
                    widget.clicked.disconnect()
            except Exception:
                pass

        self.product_widgets.clear()

        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                try:
                    item.widget().deleteLater()
                except Exception:
                    pass

        self._add_products_to_layout(self.container_layout)

    def _add_products_to_layout(self, layout):
        if not self.filtered_products:
            no_products_label = QLabel("Товары не найдены")
            no_products_label.setAlignment(Qt.AlignCenter)
            no_products_label.setFont(QFont("Times New Roman", 16))
            layout.addWidget(no_products_label)
            return

        for product in self.filtered_products:
            try:
                item = ProductItemWidget(product)
                item.setFixedHeight(210)

                item.clicked.connect(
                    lambda checked=False, p=product: self._on_product_click(p, checked)
                )

                layout.addWidget(item)
                self.product_widgets.append(item)

            except Exception:
                continue

    def _on_product_click(self, product, checked=False):
        if callable(self.open_edit_product):
            try:
                sku = product.get("sku")
                if sku:
                    self.open_edit_product(sku, product)
            except Exception:
                pass

    def _open_orders(self):
        if callable(self.open_orders):
            try:
                self.open_orders()
            except Exception:
                pass

    def _add_product(self):
        if callable(self.open_add_product):
            try:
                self.open_add_product()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть форму добавления: {str(e)}")

    def update_products(self, new_products):
        self.products = new_products
        self.apply_filters()

    def refresh(self):
        self.apply_filters()