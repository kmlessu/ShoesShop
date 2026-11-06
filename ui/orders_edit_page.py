from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QDateEdit, QGridLayout, QMessageBox,
    QCompleter, QListView, QFrame, QSpacerItem, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QSpinBox, QDialog, QDialogButtonBox
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QDate, QTimer

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


class ProductSelectionDialog(QDialog):
    def __init__(self, parent=None, existing_items=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор товаров")
        self.setModal(True)
        self.setMinimumSize(700, 500)

        # Существующие товары для редактирования
        self.existing_items = existing_items or []
        self.selected_items = self.existing_items.copy()

        layout = QVBoxLayout(self)

        # Таблица товаров
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Артикул", "Название", "Доступно", "Количество в заказе"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.table)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_products()

    def load_products(self):
        products = db.get_all_products()
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            sku = product.get('sku', '')

            # Проверяем, есть ли этот товар уже в выбранных
            existing_qty = 0
            for item in self.selected_items:
                if item['sku'] == sku:
                    existing_qty = item['quantity']
                    break

            # Артикул
            sku_item = QTableWidgetItem(sku)
            sku_item.setFlags(sku_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, sku_item)

            # Название
            name_item = QTableWidgetItem(product.get('name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, name_item)

            # Доступное количество на складе
            quantity_on_stock = product.get('quantity', 0)
            # ДОСТУПНО = Текущее на складе + Уже в заказе
            available_qty = quantity_on_stock + existing_qty
            stock_item = QTableWidgetItem(str(available_qty))
            stock_item.setFlags(stock_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, stock_item)

            # Спинбокс для выбора количества
            spinbox = QSpinBox()
            spinbox.setRange(0, available_qty)  # Максимум = доступное количество
            spinbox.setValue(existing_qty)
            spinbox.setEnabled(available_qty > 0)
            spinbox.valueChanged.connect(lambda value, s=sku, r=row, sq=quantity_on_stock:
                                         self.on_quantity_changed(s, value, r, sq))
            self.table.setCellWidget(row, 3, spinbox)

    def on_quantity_changed(self, sku, value, row, stock_qty):
        # Обновляем или добавляем товар в список
        self.selected_items = [item for item in self.selected_items if item['sku'] != sku]

        if value > 0:
            # Получаем информацию о товаре
            product = db.get_product_by_sku(sku)
            if product:
                self.selected_items.append({
                    'sku': sku,
                    'quantity': value,
                    'name': product.get('name', ''),
                    'price': product.get('price', 0)
                })

    def get_selected_items(self):
        # Возвращаем только товары с количеством > 0
        return [item for item in self.selected_items if item['quantity'] > 0]


class OrderEditPage(QWidget):
    def __init__(self, is_edit=False, order_id=None, order=None, go_back=None,
                 orders_storage=None, refresh_list=None):
        super().__init__()

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#FFFFFF"))
        self.setPalette(palette)

        self.is_edit = is_edit
        self.order_id = order_id
        self.order = order
        self.go_back = go_back
        self.orders_storage = orders_storage
        self.refresh_list = refresh_list

        # Список выбранных товаров
        self.selected_items = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_container = QWidget()
        title_container.setStyleSheet("background-color: #7FFF00;")
        title_container.setFixedHeight(80)

        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Редактирование заказа" if is_edit else "Добавление заказа")
        title.setFont(QFont("Times New Roman", 28))
        title.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: black;
            }
        """)
        title.setAlignment(Qt.AlignCenter)

        title_layout.addWidget(title, alignment=Qt.AlignCenter)

        main_layout.addWidget(title_container)

        main_content_widget = QWidget()
        main_content_layout = QVBoxLayout(main_content_widget)
        main_content_layout.setContentsMargins(20, 40, 20, 40)
        main_content_layout.setSpacing(20)

        main_content_layout.addSpacing(20)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(30)
        form_layout.setVerticalSpacing(15)

        field_style = """
            padding: 8px;
            border: 2px solid black;
            border-radius: 8px;
            font-family: 'Times New Roman';
            font-size: 14px;
            background-color: white;
            min-width: 350px;
        """

        row = 0

        # Кнопка выбора товаров
        label1 = QLabel("Товары:")
        label1.setFont(QFont("Times New Roman", 16))
        form_layout.addWidget(label1, row, 0, Qt.AlignRight)

        btn_select = QPushButton("Выбрать/Изменить товары...")
        btn_select.setFixedHeight(34)
        btn_select.setMinimumWidth(350)
        btn_select.setStyleSheet(f"""
            QPushButton {{
                {field_style}
                text-align: left;
            }}
        """)
        btn_select.clicked.connect(self.select_products)
        form_layout.addWidget(btn_select, row, 1)
        row += 1

        # Таблица выбранных товаров
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)  # Убрали столбец Действие
        self.products_table.setHorizontalHeaderLabels(["Артикул", "Название", "Количество"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setMaximumHeight(150)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        form_layout.addWidget(self.products_table, row, 0, 1, 2)
        row += 1

        label2 = QLabel("Статус заказа:")
        label2.setFont(QFont("Times New Roman", 16))
        form_layout.addWidget(label2, row, 0, Qt.AlignRight)

        self.status_field = FixedComboBox()
        self.status_field.addItems([
            "Новый",
            "В обработке",
            "Собран",
            "Передан в доставку",
            "Доставлен",
            "Готов к выдаче",
            "Выдан",
            "Отменен"
        ])
        self.status_field.setFixedHeight(34)
        self.status_field.setMinimumWidth(350)
        self.status_field.setStyleSheet(f"""
            QComboBox {{
                {field_style}
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox QAbstractItemView {{
                border-radius: 8px;
                background-color: white;
                selection-background-color: #7FFF00;
                selection-color: black;
                min-width: 350px;
            }}
        """)
        form_layout.addWidget(self.status_field, row, 1)
        row += 1

        label3 = QLabel("Адрес пункта выдачи:")
        label3.setFont(QFont("Times New Roman", 16))
        form_layout.addWidget(label3, row, 0, Qt.AlignRight)

        self.delivery_point_field = QLineEdit()
        self._setup_address_autocomplete()
        self.delivery_point_field.setFixedHeight(34)
        self.delivery_point_field.setMinimumWidth(350)
        self.delivery_point_field.setStyleSheet(field_style)
        form_layout.addWidget(self.delivery_point_field, row, 1)
        row += 1

        label4 = QLabel("Дата заказа:")
        label4.setFont(QFont("Times New Roman", 16))
        form_layout.addWidget(label4, row, 0, Qt.AlignRight)

        self.order_date_field = QDateEdit()
        self.order_date_field.setCalendarPopup(True)
        self.order_date_field.setDate(QDate.currentDate())
        self.order_date_field.setDisplayFormat("dd.MM.yyyy")
        self.order_date_field.setFixedHeight(34)
        self.order_date_field.setMinimumWidth(350)
        self.order_date_field.setStyleSheet(f"""
            QDateEdit {{
                {field_style}
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 30px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)
        form_layout.addWidget(self.order_date_field, row, 1)
        row += 1

        label5 = QLabel("Дата выдачи:")
        label5.setFont(QFont("Times New Roman", 16))
        form_layout.addWidget(label5, row, 0, Qt.AlignRight)

        self.delivery_date_field = QDateEdit()
        self.delivery_date_field.setCalendarPopup(True)
        self.delivery_date_field.setDate(QDate.currentDate().addDays(3))
        self.delivery_date_field.setDisplayFormat("dd.MM.yyyy")
        self.delivery_date_field.setFixedHeight(34)
        self.delivery_date_field.setMinimumWidth(350)
        self.delivery_date_field.setStyleSheet(f"""
            QDateEdit {{
                {field_style}
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 30px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)
        form_layout.addWidget(self.delivery_date_field, row, 1)

        main_content_layout.addLayout(form_layout)

        main_content_layout.addSpacing(40)

        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignCenter)
        btns.setSpacing(20)

        BUTTON_STYLE = """
        QPushButton {
            background-color: #00FA9A;
            border: 2px solid black;
            border-radius: 0px;
        }
        QPushButton:hover {
            background-color: #7CFC00;
        }
        """

        back = QPushButton("← Назад")
        back.setFixedSize(130, 34)
        back.setFont(QFont("Times New Roman", 18))
        back.setStyleSheet(BUTTON_STYLE)
        back.clicked.connect(self.go_back)
        btns.addWidget(back)

        save = QPushButton("Сохранить")
        save.setFixedSize(140, 34)
        save.setFont(QFont("Times New Roman", 18))
        save.setStyleSheet(BUTTON_STYLE)
        save.clicked.connect(self._save_clicked)
        btns.addWidget(save)

        if is_edit:
            delete = QPushButton("Удалить")
            delete.setFixedSize(140, 34)
            delete.setFont(QFont("Times New Roman", 18))
            delete.setStyleSheet(BUTTON_STYLE)
            delete.clicked.connect(self._delete)
            btns.addWidget(delete)

        main_content_layout.addLayout(btns)

        main_content_layout.addStretch()

        main_layout.addWidget(main_content_widget)

        if is_edit and order:
            self._load_order(order)

    def _setup_address_autocomplete(self):
        try:
            addresses = db.get_warehouse_addresses()
            if addresses:
                completer = QCompleter(addresses)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                self.delivery_point_field.setCompleter(completer)

                if addresses:
                    self.delivery_point_field.setText(addresses[0])
        except:
            pass

    def select_products(self):
        dialog = ProductSelectionDialog(self, self.selected_items)
        if dialog.exec() == QDialog.Accepted:
            self.selected_items = dialog.get_selected_items()
            self.update_products_table()

    def update_products_table(self):
        self.products_table.setRowCount(len(self.selected_items))

        for row, item in enumerate(self.selected_items):
            # Артикул
            sku_item = QTableWidgetItem(item['sku'])
            sku_item.setFlags(sku_item.flags() & ~Qt.ItemIsEditable)
            self.products_table.setItem(row, 0, sku_item)

            # Название
            name_item = QTableWidgetItem(item['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.products_table.setItem(row, 1, name_item)

            # Количество
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
            self.products_table.setItem(row, 2, qty_item)

    def _load_order(self, o):
        self._warehouse_id = o.get("warehouse_id")
        self._customer_id = o.get("customer_id")

        # Загружаем товары из существующего заказа
        if self.order_id:
            try:
                items = db.get_order_items(self.order_id)
                for item in items:
                    self.selected_items.append({
                        'sku': item.get('sku'),
                        'quantity': item.get('quantity', 0),
                        'name': item.get('name', ''),
                        'price': item.get('price', 0)
                    })
                self.update_products_table()
            except Exception as e:
                print(f"Ошибка загрузки товаров заказа: {e}")

        status = o.get("status", "")
        index = self.status_field.findText(status)
        if index >= 0:
            self.status_field.setCurrentIndex(index)

        self.delivery_point_field.setText(o.get("delivery_point", ""))

        order_date_str = o.get("order_date", "")
        if order_date_str:
            try:
                from datetime import datetime
                dt = datetime.strptime(order_date_str, "%Y-%m-%d")
                order_date = QDate(dt.year, dt.month, dt.day)
                if order_date.isValid():
                    self.order_date_field.setDate(order_date)
            except:
                self.order_date_field.setDate(QDate.currentDate())

        delivery_date_str = o.get("delivery_date", "")
        if delivery_date_str:
            try:
                from datetime import datetime
                dt = datetime.strptime(delivery_date_str, "%Y-%m-%d")
                delivery_date = QDate(dt.year, dt.month, dt.day)
                if delivery_date.isValid():
                    self.delivery_date_field.setDate(delivery_date)
            except:
                self.delivery_date_field.setDate(QDate.currentDate().addDays(3))

    def _generate_pickup_code(self):
        try:
            query = """
            SELECT MAX(CAST(pickup_code AS INTEGER)) as max_code 
            FROM orders 
            WHERE pickup_code ~ '^[0-9]+$'
            """
            result = db.execute_query(query)

            if result and result[0]['max_code']:
                max_code = int(result[0]['max_code'])
                if max_code < 911:
                    return "911"
                else:
                    return str(max_code + 1)
            else:
                return "911"

        except Exception:
            return "911"

    def _save_clicked(self):
        QTimer.singleShot(10, self._save_impl)

    def _save_impl(self):
        if not self.selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один товар")
            return

        if not self.delivery_point_field.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите адрес пункта выдачи")
            return

        try:
            # Проверяем наличие товаров на складе
            for item in self.selected_items:
                sku = item['sku']
                order_quantity = item['quantity']

                product = db.get_product_by_sku(sku)
                if not product:
                    QMessageBox.warning(self, "Ошибка", f"Товар с артикулом '{sku}' не найден в БД")
                    return

                available_quantity = product.get('quantity', 0)

                # Проверяем, есть ли этот товар в текущем заказе (для редактирования)
                if self.is_edit:
                    try:
                        old_items = db.get_order_items(self.order_id)
                        old_qty = 0
                        for old_item in old_items:
                            if old_item['sku'] == sku:
                                old_qty = old_item['quantity']
                                break

                        # Доступное количество = текущий склад + старое количество из заказа
                        available_quantity += old_qty
                    except:
                        pass

                if order_quantity > available_quantity:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Товар {sku}: заказывается {order_quantity}, но доступно только {available_quantity}")
                    return

            if self.is_edit:
                pickup_code = self.order.get("pickup_code") if self.order else ""
                if not pickup_code:
                    pickup_code = self._generate_pickup_code()
            else:
                pickup_code = self._generate_pickup_code()

            new_data = {
                "id": self.order_id if self.is_edit else 0,
                "pickup_code": pickup_code,
                "status": self.status_field.currentText(),
                "delivery_point": self.delivery_point_field.text().strip(),
                "order_date": self.order_date_field.date().toString("yyyy-MM-dd"),
                "delivery_date": self.delivery_date_field.date().toString("yyyy-MM-dd"),
                "warehouse_id": getattr(self, '_warehouse_id', None),
                "customer_id": getattr(self, '_customer_id', None)
            }

            success = False
            order_id = None

            if self.is_edit:
                success = db.update_order(new_data)
                if success:
                    # Получаем старые товары для восстановления количества
                    old_items = db.get_order_items(self.order_id)

                    # Восстанавливаем количество старых товаров на складе
                    for old_item in old_items:
                        db.update_product_quantity(old_item['sku'], old_item['quantity'])

                    # Удаляем старые товары
                    db.execute_update("DELETE FROM order_items WHERE order_id = %s", (self.order_id,))

                    # Добавляем новые товары и обновляем склад
                    for item in self.selected_items:
                        db.add_order_item(self.order_id, item['sku'], item['quantity'])
                        db.update_product_quantity(item['sku'], -item['quantity'])

                    order_id = self.order_id
                    QMessageBox.information(self, "Успех", "Заказ успешно обновлен")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить заказ")
            else:
                order_id = db.add_order(new_data)

                if order_id and order_id > 0:
                    success = True
                    self.order_id = order_id

                    for item in self.selected_items:
                        sku = item['sku']
                        quantity = item['quantity']

                        item_success = db.add_order_item(order_id, sku, quantity)

                        if item_success:
                            # Уменьшаем количество на складе
                            db.update_product_quantity(sku, -quantity)

                    QMessageBox.information(self, "Успех", f"Заказ успешно добавлен (Код выдачи: {pickup_code})")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить заказ")
                    success = False

            if success and order_id:
                if self.refresh_list:
                    self.refresh_list()

                if self.go_back:
                    QTimer.singleShot(300, self.go_back)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def _delete(self):
        if not self.is_edit:
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить заказ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:  # ИСПРАВЛЕНО: QMessageBox.Yes вместо QDialog.Yes
            try:
                items = db.get_order_items(self.order_id)
                for item in items:
                    db.update_product_quantity(item['sku'], item['quantity'])
            except Exception:
                pass

            success = db.delete_order(self.order_id)
            if success:
                QMessageBox.information(self, "Успех", "Заказ успешно удален")
                if self.refresh_list:
                    self.refresh_list()
                if self.go_back:
                    self.go_back()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить заказ")