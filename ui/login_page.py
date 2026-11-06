from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QFont, QColor, QPixmap
from PySide6.QtCore import Signal, Qt


class LoginPage(QWidget):
    login_pressed = Signal(str, str)
    guest_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(900, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QMainWindow {
                background-color: white;
            }
            QDialog {
                background-color: white;
            }
        """)

        self.init_ui()

    def init_ui(self):
        base_font = QFont("Times New Roman", 12)
        self.setFont(base_font)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("white"))
        self.setPalette(palette)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)

        form_container = QWidget()
        form_container.setStyleSheet("background-color: white;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(25)

        logo_label = QLabel()
        try:
            pixmap = QPixmap("resources/logo.png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                logo_label.setText("LOGO")
                logo_label.setFont(QFont("Times New Roman", 36, QFont.Bold))
        except:
            logo_label.setText("LOGO")
            logo_label.setFont(QFont("Times New Roman", 36, QFont.Bold))

        logo_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        title = QLabel("Вход в систему")
        title.setFont(QFont("Times New Roman", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title, alignment=Qt.AlignCenter)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.login_input.setFixedWidth(600)
        self.login_input.setFixedHeight(45)
        self.login_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid black;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 16px;
                background-color: white;
            }
        """)
        form_layout.addWidget(self.login_input, alignment=Qt.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(600)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid black;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 16px;
                background-color: white;
            }
        """)
        form_layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_login = QPushButton("Войти")
        self.btn_login.setFixedSize(180, 45)
        self.btn_login.setFont(QFont("Times New Roman", 18))
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
                font-family: 'Times New Roman';
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #7FFF00;
            }
        """)
        self.btn_login.clicked.connect(self._on_login_clicked)

        self.btn_guest = QPushButton("Войти как гость")
        self.btn_guest.setFixedSize(200, 45)
        self.btn_guest.setFont(QFont("Times New Roman", 16))
        self.btn_guest.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                border: 2px solid black;
                border-radius: 0px;
                font-family: 'Times New Roman';
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #7FFF00;
            }
        """)
        self.btn_guest.clicked.connect(self._on_guest_clicked)

        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_guest)
        form_layout.addLayout(btn_layout)

        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        main_layout.insertStretch(0, 1)
        main_layout.addStretch(1)

    def _on_login_clicked(self):
        login = self.login_input.text().strip()
        password = self.password_input.text()
        self.login_pressed.emit(login, password)

    def _on_guest_clicked(self):
        self.guest_pressed.emit()