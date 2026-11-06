from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QComboBox, QFileDialog, QFrame, QMessageBox, QListView
)
from PySide6.QtGui import QFont, QPixmap, QColor, QIntValidator
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
import os
import re

from database import db


class PriceLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("0,00")

        regex = QRegularExpression(r"^\d*[,]?\d{0,2}$")
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if not self.text():
            self.setText("0,00")
            self.setCursorPosition(0)
        else:
            pass

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        text = self.text()
        if text:
            self._format_price(text)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def _format_price(self, text):
        if not text:
            self.setText("0,00")
            return

        clean_text = re.sub(r'[^\d,]', '', text)

        if not clean_text:
            self.setText("0,00")
            return

        if ',' in clean_text:
            parts = clean_text.split(',')
            if len(parts) == 2:
                rubles = parts[0] if parts[0] else '0'
                kopecks = parts[1][:2].ljust(2, '0')
                formatted = f"{rubles},{kopecks}"
                if formatted != text:
                    self.setText(formatted)
        else:
            if len(clean_text) <= 2:
                formatted = f"0,{clean_text.zfill(2)}"
            else:
                rubles = clean_text[:-2]
                kopecks = clean_text[-2:].zfill(2)
                formatted = f"{rubles},{kopecks}"

            if formatted != text:
                self.setText(formatted)


class FixedComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        view = QListView()
        view.setMinimumHeight(70)
        self.setView(view)

    def showPopup(self):
        self.view().setMinimumWidth(self.width() + 40)
        super().showPopup()


class LettersOnlyLineEdit(QLineEdit):
    """Поле ввода, которое принимает только буквы, пробелы и некоторые символы"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Регулярное выражение: только буквы (русские и английские), пробелы, дефисы, апострофы, точки
        regex = QRegularExpression(r'^[а-яА-ЯёЁa-zA-Z\s\-\.\',]*$')
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)

    def keyPressEvent(self, event):
        # Дополнительная проверка: игнорируем цифровые клавиши
        if event.text().isdigit():
            return
        super().keyPressEvent(event)


class PositiveIntLineEdit(QLineEdit):
    """Поле ввода, которое принимает только положительные целые числа"""

    def __init__(self, parent=None):
        super().__init__(parent)
        validator = QIntValidator(0, 999999, self)
        self.setValidator(validator)

    def keyPressEvent(self, event):
        # Игнорируем минус
        if event.text() == '-':
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # Проверяем, что число положительное
        text = self.text()
        if text and int(text) < 0:
            self.setText("0")


class ProductEditPage(QWidget):
    def __init__(self, is_edit=False, sku=None, product=None, go_back=None,
                 products_storage=None, refresh_list=None):
        super().__init__()

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#FFFFFF"))
        self.setPalette(palette)

        self.is_edit = is_edit
        self.sku = sku
        self.product = product
        self.go_back = go_back
        self.products_storage = products_storage
        self.refresh_list = refresh_list

        self.photo_path = product.get("photo_filename") if product else None

        layout = QVBoxLayout(self)

        title = QLabel("Редактирование товара" if is_edit else "Добавление товара")
        title.setFont(QFont("Times New Roman", 28))
        title.setStyleSheet("background-color: #7FFF00")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QVBoxLayout()
        layout.addLayout(form)

        photo_row = QHBoxLayout()
        photo_lbl = QLabel("Фото:")
        photo_lbl.setFixedWidth(150)
        photo_row.addWidget(photo_lbl)

        self.photo_frame = QFrame()
        self.photo_frame.setFrameShape(QFrame.Box)
        self.photo_frame.setFixedSize(300, 200)

        self.photo_preview = QLabel()
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self._update_photo_preview()

        pf_layout = QVBoxLayout(self.photo_frame)
        pf_layout.addWidget(self.photo_preview)

        photo_row.addWidget(self.photo_frame)

        self.btn_choose_photo = QPushButton("Выбрать фото")
        self.btn_choose_photo.setFixedHeight(34)
        self.btn_choose_photo.setFont(QFont("Times New Roman", 14))
        self.btn_choose_photo.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #7CFC00;
            }
        """)
        self.btn_choose_photo.clicked.connect(self._choose_photo)
        photo_row.addWidget(self.btn_choose_photo)

        form.addLayout(photo_row)

        # 🔴 ИЗМЕНЕНО: используем LettersOnlyLineEdit для текстовых полей
        self.name_field = LettersOnlyLineEdit()
        self.description_field = QTextEdit()
        self.category_field = FixedComboBox()
        self.manufacturer_field = FixedComboBox()
        self.supplier_field = LettersOnlyLineEdit()

        self.price_field = PriceLineEdit()

        self.unit_field = QLineEdit("пар.")
        self.unit_field.setReadOnly(True)

        # 🔴 ИЗМЕНЕНО: используем PositiveIntLineEdit для количества
        self.stock_field = PositiveIntLineEdit()

        # 🔴 ИЗМЕНЕНО: используем PositiveIntLineEdit для скидки
        self.discount_field = PositiveIntLineEdit()

        self._populate_comboboxes()

        def add_row(label, widget, required=False):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(150)
            lbl.setFont(QFont("Times New Roman", 16))
            if required:
                lbl.setText(label + " *")
            row.addWidget(lbl)

            if isinstance(widget, LettersOnlyLineEdit):
                widget.setFixedHeight(34)
                widget.setMinimumWidth(350)
                widget.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid black;
                        border-radius: 8px;
                        font-family: 'Times New Roman';
                        font-size: 14px;
                        background-color: white;
                        min-width: 350px;
                    }
                """)
            elif isinstance(widget, PositiveIntLineEdit):
                widget.setFixedHeight(34)
                widget.setMinimumWidth(350)
                widget.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid black;
                        border-radius: 8px;
                        font-family: 'Times New Roman';
                        font-size: 14px;
                        background-color: white;
                        min-width: 350px;
                    }
                """)
                if widget == self.stock_field:
                    widget.setPlaceholderText("Только положительные числа")
                elif widget == self.discount_field:
                    widget.setPlaceholderText("0-100")
            elif isinstance(widget, QLineEdit):
                widget.setFixedHeight(34)
                widget.setMinimumWidth(350)
                if widget is self.unit_field:
                    widget.setStyleSheet("""
                        QLineEdit {
                            padding: 8px;
                            border: 2px solid #666;
                            border-radius: 8px;
                            font-family: 'Times New Roman';
                            font-size: 14px;
                            background-color: #f0f0f0;
                            color: #666;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QLineEdit {
                            padding: 8px;
                            border: 2px solid black;
                            border-radius: 8px;
                            font-family: 'Times New Roman';
                            font-size: 14px;
                            background-color: white;
                            min-width: 350px;
                        }
                    """)
            elif isinstance(widget, FixedComboBox):
                widget.setFixedHeight(34)
                widget.setMinimumWidth(350)
                widget.setStyleSheet("""
                    QComboBox {
                        padding: 8px;
                        border: 2px solid black;
                        border-radius: 8px;
                        font-family: 'Times New Roman';
                        font-size: 14px;
                        background-color: white;
                        min-width: 350px;
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
                        min-width: 350px;
                    }
                """)
            elif isinstance(widget, QTextEdit):
                widget.setFixedHeight(80)
                widget.setMinimumWidth(350)
                widget.setStyleSheet("""
                    QTextEdit {
                        padding: 8px;
                        border: 2px solid black;
                        border-radius: 8px;
                        font-family: 'Times New Roman';
                        font-size: 14px;
                        background-color: white;
                        min-width: 350px;
                    }
                """)

            row.addWidget(widget)
            form.addLayout(row)

        # Обязательные поля отмечены звездочкой
        add_row("Наименование:", self.name_field, required=True)
        add_row("Описание:", self.description_field)
        add_row("Категория:", self.category_field)
        add_row("Производитель:", self.manufacturer_field)
        add_row("Поставщик:", self.supplier_field)
        add_row("Цена:", self.price_field, required=True)
        add_row("Ед.:", self.unit_field)
        add_row("Кол-во:", self.stock_field, required=True)
        add_row("Скидка:", self.discount_field)

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
        save.clicked.connect(self._save)
        btns.addWidget(save)

        if is_edit:
            delete = QPushButton("Удалить")
            delete.setFixedSize(140, 34)
            delete.setFont(QFont("Times New Roman", 18))
            delete.setStyleSheet(BUTTON_STYLE)
            delete.clicked.connect(self._delete)
            btns.addWidget(delete)

        layout.addLayout(btns)

        if is_edit and product:
            self._load_product(product)
        else:
            self.price_field.setText("0,00")
            self.stock_field.setText("0")
            self.discount_field.setText("0")

    def _populate_comboboxes(self):
        categories = db.get_all_categories()
        for category in categories:
            self.category_field.addItem(category)

        manufacturers = db.get_all_manufacturers()
        for manufacturer in manufacturers:
            self.manufacturer_field.addItem(manufacturer)

    def _update_photo_preview(self):
        if self.photo_path and os.path.exists(self.photo_path):
            pix = QPixmap(self.photo_path)
            self.photo_preview.setPixmap(
                pix.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.photo_preview.setText("Нет фото")
            self.photo_preview.setFont(QFont("Times New Roman", 16))

    def _choose_photo(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Выберите фото", "", "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if fname:
            self.photo_path = fname
            self._update_photo_preview()

    def _load_product(self, p):
        self.name_field.setText(p.get("name", ""))
        self.description_field.setText(p.get("description", ""))
        self.supplier_field.setText(p.get("supplier", ""))

        price_value = p.get("price", 0)

        price_str = f"{price_value:.2f}"
        price_formatted = price_str.replace('.', ',')
        self.price_field.setText(price_formatted)

        self.stock_field.setText(str(p.get("quantity", "0")))
        self.discount_field.setText(str(p.get("discount", "0")))

        category = p.get("category", "")
        index = self.category_field.findText(category)
        if index >= 0:
            self.category_field.setCurrentIndex(index)

        manufacturer = p.get("manufacturer", "")
        index = self.manufacturer_field.findText(manufacturer)
        if index >= 0:
            self.manufacturer_field.setCurrentIndex(index)

    def _save(self):
        # Проверка обязательных полей
        if not self.name_field.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите наименование товара")
            self.name_field.setFocus()
            return

        price_text = self.price_field.text().strip()
        if not price_text or price_text == "0,00":
            QMessageBox.warning(self, "Ошибка", "Введите цену товара")
            self.price_field.setFocus()
            return

        stock_text = self.stock_field.text().strip()
        if not stock_text:
            QMessageBox.warning(self, "Ошибка", "Введите количество товара")
            self.stock_field.setFocus()
            return

        # 🔴 ПРОВЕРКА ОТРИЦАТЕЛЬНОГО КОЛИЧЕСТВА
        try:
            stock_value = int(stock_text)
            if stock_value < 0:
                QMessageBox.warning(self, "Ошибка", "Количество не может быть отрицательным")
                self.stock_field.setFocus()
                self.stock_field.setText("0")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть числом")
            self.stock_field.setFocus()
            return

        try:
            discount = self.discount_field.text().strip()
            stock = self.stock_field.text().strip()

            try:
                price_input = price_text.replace(',', '.')
                price_float = float(price_input)
                price_int = int(round(price_float))
                if price_int <= 0:
                    QMessageBox.warning(self, "Ошибка", "Цена должна быть больше 0")
                    self.price_field.setFocus()
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Цена должна быть числом (например: 4550,00 или 4550,80)")
                self.price_field.setFocus()
                return

            discount_int = 0
            if discount:
                try:
                    discount_int = int(discount)
                    if discount_int < 0:
                        QMessageBox.warning(self, "Ошибка", "Скидка не может быть отрицательной")
                        self.discount_field.setFocus()
                        self.discount_field.setText("0")
                        return
                    if discount_int > 100:
                        QMessageBox.warning(self, "Ошибка", "Скидка не может быть больше 100%")
                        self.discount_field.setFocus()
                        self.discount_field.setText("100")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Скидка должна быть числом")
                    self.discount_field.setFocus()
                    return

            quantity_int = 0
            if stock:
                try:
                    quantity_int = int(stock)
                    if quantity_int < 0:
                        QMessageBox.warning(self, "Ошибка", "Количество не может быть отрицательным")
                        self.stock_field.setFocus()
                        self.stock_field.setText("0")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Количество должно быть числом")
                    self.stock_field.setFocus()
                    return

            new_data = {
                "sku": self.sku if self.is_edit else self._generate_sku(),
                "name": self.name_field.text().strip(),
                "description": self.description_field.toPlainText().strip(),
                "category": self.category_field.currentText(),
                "manufacturer": self.manufacturer_field.currentText(),
                "supplier": self.supplier_field.text().strip(),
                "price": price_int,
                "unit": "пар.",
                "quantity": quantity_int,
                "discount": discount_int,
                "photo_filename": self.photo_path
            }

            success = False
            if self.is_edit:
                success = db.update_product(new_data)
                if success:
                    QMessageBox.information(self, "Успех", "Товар успешно обновлен")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить товар")
            else:
                success = db.add_product(new_data)
                if success:
                    QMessageBox.information(self, "Успех", "Товар успешно добавлен")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить товар")

            if success and self.refresh_list:
                self.refresh_list()

            if success and self.go_back:
                self.go_back()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def _generate_sku(self):
        import string
        import random
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=3))
        return f"{letters}{numbers}"

    def _delete(self):
        if not self.is_edit:
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить товар '{self.name_field.text()}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = db.delete_product(self.sku)
            if success:
                QMessageBox.information(self, "Успех", "Товар успешно удален")
                if self.refresh_list:
                    self.refresh_list()
                if self.go_back:
                    self.go_back()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить товар")