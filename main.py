import sys
import os
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer

try:
    from ui.login_page import LoginPage
    from ui.admin_page import AdminPage
    from ui.manager_page import ManagerPage
    from ui.product_edit_page import ProductEditPage
    from ui.orders_page_admin import OrdersPageAdmin
    from ui.orders_edit_page import OrderEditPage
    from ui.products_page import ProductsPage
    from database import db
except ImportError as e:
    QMessageBox.critical(None, "Ошибка импорта", f"Не удалось импортировать модули: {e}")
    sys.exit(1)


def link_photos_to_products():
    products = db.get_all_products()
    resources_dir = "resources"

    if not os.path.exists(resources_dir):
        return

    photo_mapping = {
        "А112Т4": "1.jpg",
        "F635R4": "2.jpg",
        "H782T5": "3.jpg",
        "G783F5": "4.jpg",
        "J384T6": "5.jpg",
        "D572U8": "6.jpg",
        "F572H7": "7.jpg",
        "D329H3": "8.jpg",
        "B320R5": "9.jpg",
        "G432E4": "10.jpg",
        "S213E3": "11.jpg",
        "E482R4": "12.jpg",
        "S634B5": "13.jpg",
        "K345R4": "14.jpg",
        "O754F4": "15.jpg",
        "G531F4": "16.jpg",
        "J542F5": "17.jpg",
        "B431R5": "18.jpg",
        "P764G4": "19.jpg",
        "C436G5": "20.jpg",
        "F427R5": "21.jpg",
        "N457T5": "22.jpg",
        "D364R4": "23.jpg",
        "S326R5": "24.jpg",
        "L754R4": "25.jpg",
        "M542T5": "26.jpg",
        "D268G5": "27.jpg",
        "T324F5": "28.jpg",
        "K358H6": "29.jpg",
        "H535R5": "30.jpg"
    }

    for product in products:
        sku = product.get('sku', '')
        if sku in photo_mapping:
            photo_name = photo_mapping[sku]
            photo_path = os.path.join(resources_dir, photo_name)

            if os.path.exists(photo_path):
                query = "UPDATE products SET photo_filename = %s WHERE sku = %s"
                db.execute_update(query, (photo_path, sku))

    for product in products:
        sku = product.get('sku', '')
        if sku not in photo_mapping:
            default_photo = os.path.join(resources_dir, "picture.png")
            if os.path.exists(default_photo):
                query = "UPDATE products SET photo_filename = %s WHERE sku = %s"
                db.execute_update(query, (default_photo, sku))


class MainWindow:
    def __init__(self):
        self.app = QApplication(sys.argv)

        if os.path.exists("resources/logo.png"):
            self.app.setWindowIcon(QIcon("resources/logo.png"))

        if db.connection is None:
            QMessageBox.critical(None, "Ошибка",
                                 "Не удалось подключиться к базе данных!\n"
                                 "Проверьте настройки подключения в database.py")
            sys.exit(1)

        link_photos_to_products()

        self.products_storage = db.get_all_products()
        self.orders_storage = db.get_all_orders()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setWindowTitle("Магазин обуви")
        self.stacked_widget.setMinimumSize(1200, 800)

        self.login_page = LoginPage()
        self.stacked_widget.addWidget(self.login_page)

        self.login_page.login_pressed.connect(self.handle_login)
        self.login_page.guest_pressed.connect(self.handle_guest_login)

        self.stacked_widget.show()

        self.app.aboutToQuit.connect(self.cleanup)

    def run(self):
        return self.app.exec()

    def cleanup(self):
        db.close()

    def handle_login(self, login, password):
        QTimer.singleShot(100, lambda: self._process_login(login, password))

    def _process_login(self, login, password):
        user = db.get_user_by_credentials(login, password)

        if user:
            role_name = user.get('role_name', 'Гость')
            full_name = user.get('full_name', 'Пользователь')

            if role_name == 'Администратор':
                self.show_admin_page(full_name, role_name)
            elif role_name == 'Менеджер':
                self.show_manager_page(full_name, role_name)
            elif role_name == 'Авторизованный клиент':
                self.show_products_page(full_name, "Клиент", full_name)
            else:
                QMessageBox.warning(None, "Ошибка", "Неизвестная роль пользователя")
        else:
            QMessageBox.warning(None, "Ошибка", "Неверный логин или пароль")

    def handle_guest_login(self):
        self.products_storage = db.get_all_products()
        QTimer.singleShot(100, lambda: self._show_guest_page())

    def _show_guest_page(self):
        for i in range(self.stacked_widget.count() - 1, -1, -1):
            widget = self.stacked_widget.widget(i)
            if widget != self.login_page:
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()

        self.guest_page = ProductsPage(
            role_name="Гость",
            products=self.products_storage,
            full_name="Гость"
        )

        self.guest_page.back_requested.connect(self.show_login_page)

        self.stacked_widget.addWidget(self.guest_page)
        self.stacked_widget.setCurrentWidget(self.guest_page)

    def show_admin_page(self, full_name, role_name):
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != self.login_page:
            self.stacked_widget.removeWidget(current_widget)
            if current_widget:
                current_widget.deleteLater()

        self.admin_page = AdminPage(
            full_name=full_name,
            go_back=None,
            open_orders=lambda: self.show_admin_orders_page(full_name),
            open_add_product=lambda: self.show_product_edit_page(is_edit=False),
            open_edit_product=lambda sku, product: self.show_product_edit_page(sku=sku, product=product, is_edit=True),
            products=self.products_storage
        )

        self.admin_page.back_to_login.connect(self.show_login_page)

        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            if widget != self.login_page:
                widget.deleteLater()

        self.stacked_widget.addWidget(self.admin_page)
        self.stacked_widget.setCurrentWidget(self.admin_page)

    def show_manager_page(self, full_name, role_name):
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != self.login_page:
            self.stacked_widget.removeWidget(current_widget)
            if current_widget:
                current_widget.deleteLater()

        self.manager_page = ManagerPage(
            full_name=full_name,
            go_back=None,
            open_orders=lambda: self.show_manager_orders_page(full_name)
        )

        self.manager_page.back_to_login.connect(self.show_login_page)

        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            if widget != self.login_page:
                widget.deleteLater()

        self.stacked_widget.addWidget(self.manager_page)
        self.stacked_widget.setCurrentWidget(self.manager_page)

    def show_products_page(self, role_name, user_type, full_name=None):
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != self.login_page:
            self.stacked_widget.removeWidget(current_widget)
            if current_widget:
                current_widget.deleteLater()

        display_name = full_name if full_name else role_name

        products_page = ProductsPage(
            role_name=display_name,
            products=self.products_storage,
            full_name=display_name
        )

        products_page.back_requested.connect(self.show_login_page)

        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            if widget != self.login_page:
                widget.deleteLater()

        self.stacked_widget.addWidget(products_page)
        self.stacked_widget.setCurrentWidget(products_page)

    def show_login_page(self):
        widgets_to_remove = []
        for i in range(self.stacked_widget.count() - 1, -1, -1):
            widget = self.stacked_widget.widget(i)
            if widget != self.login_page:
                widgets_to_remove.append((i, widget))

        for i, widget in widgets_to_remove:
            self.stacked_widget.removeWidget(widget)
            if widget:
                try:
                    widget.setParent(None)
                    widget.deleteLater()
                except:
                    pass

        found_login = False
        for i in range(self.stacked_widget.count()):
            if self.stacked_widget.widget(i) == self.login_page:
                found_login = True
                break

        if not found_login:
            self.login_page = LoginPage()
            self.login_page.login_pressed.connect(self.handle_login)
            self.login_page.guest_pressed.connect(self.handle_guest_login)
            self.stacked_widget.addWidget(self.login_page)

        self.stacked_widget.setCurrentWidget(self.login_page)

    def show_admin_orders_page(self, full_name):
        self.orders_page_admin = OrdersPageAdmin(
            role_name="Администратор",
            full_name=full_name,
            go_back=lambda: self.go_back_from_admin_orders(),
            open_add_order=lambda: self.show_order_edit_page(is_edit=False),
            open_edit_order=lambda order_id: self.show_order_edit_page(order_id=order_id, is_edit=True)
        )

        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            self.stacked_widget.removeWidget(current_widget)
            if current_widget:
                current_widget.deleteLater()

        self.stacked_widget.addWidget(self.orders_page_admin)
        self.stacked_widget.setCurrentWidget(self.orders_page_admin)

    def go_back_from_admin_orders(self):
        if hasattr(self, 'admin_page') and self.admin_page:
            full_name = getattr(self.admin_page, 'full_name', "Администратор")
            self.show_admin_page(full_name, "Администратор")
        else:
            self.show_login_page()

    def show_manager_orders_page(self, full_name):
        try:
            from ui.orders_page_manager import OrdersPageManager
            orders_page = OrdersPageManager(
                role_name="Менеджер",
                full_name=full_name,
                go_back=lambda: self.go_back_from_manager_orders()
            )

            current_widget = self.stacked_widget.currentWidget()
            if current_widget:
                self.stacked_widget.removeWidget(current_widget)
                if current_widget:
                    current_widget.deleteLater()

            self.stacked_widget.addWidget(orders_page)
            self.stacked_widget.setCurrentWidget(orders_page)
        except ImportError as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить страницу заказов менеджера: {e}")

    def go_back_from_manager_orders(self):
        if hasattr(self, 'manager_page') and self.manager_page:
            full_name = getattr(self.manager_page, 'full_name', "Менеджер")
            self.show_manager_page(full_name, "Менеджер")
        else:
            self.show_login_page()

    def show_product_edit_page(self, sku=None, product=None, is_edit=False):
        if product is None and is_edit and sku:
            product = db.get_product_by_sku(sku)

        self.product_edit_page = ProductEditPage(
            is_edit=is_edit,
            sku=sku,
            product=product,
            go_back=self.go_back_from_product_edit,
            products_storage=self.products_storage,
            refresh_list=self.refresh_admin_products
        )

        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            self.stacked_widget.removeWidget(current_widget)
            if current_widget:
                current_widget.deleteLater()

        self.stacked_widget.addWidget(self.product_edit_page)
        self.stacked_widget.setCurrentWidget(self.product_edit_page)

    def go_back_from_product_edit(self):
        if hasattr(self, 'admin_page') and self.admin_page:
            full_name = getattr(self.admin_page, 'full_name', "Администратор")
            self.show_admin_page(full_name, "Администратор")
        else:
            self.show_login_page()

    def show_order_edit_page(self, order_id=None, order=None, is_edit=False):
        if order is None and is_edit and order_id:
            order = db.get_order_by_id(order_id)

        self.order_edit_page = OrderEditPage(
            is_edit=is_edit,
            order_id=order_id,
            order=order,
            go_back=self.go_back_from_order_edit,
            orders_storage=self.orders_storage,
            refresh_list=self.refresh_admin_orders
        )

        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            self.stacked_widget.removeWidget(current_widget)
            if current_widget:
                current_widget.deleteLater()

        self.stacked_widget.addWidget(self.order_edit_page)
        self.stacked_widget.setCurrentWidget(self.order_edit_page)

    def go_back_from_order_edit(self):
        if hasattr(self, 'orders_page_admin'):
            widget = self.stacked_widget.widget(self.stacked_widget.currentIndex())
            if widget:
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()

        if hasattr(self, 'admin_page'):
            full_name = getattr(self.admin_page, 'full_name', "Администратор")
            self.show_admin_orders_page(full_name)
        else:
            self.show_admin_orders_page("Администратор")

    def refresh_admin_products(self):
        self.products_storage = db.get_all_products()
        if hasattr(self, 'admin_page') and self.admin_page:
            self.admin_page.products = self.products_storage
            if hasattr(self.admin_page, 'apply_filters'):
                self.admin_page.apply_filters()

    def refresh_admin_orders(self):
        self.orders_storage = db.get_all_orders()
        if hasattr(self, 'orders_page_admin') and self.orders_page_admin:
            try:
                if hasattr(self.orders_page_admin, 'refresh_orders'):
                    self.orders_page_admin.refresh_orders()
            except Exception:
                pass


if __name__ == "__main__":
    window = MainWindow()
    sys.exit(window.run())