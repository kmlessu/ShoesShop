# Установка и запуск ShoeStore

Приложение собрано PyInstaller в режиме onedir. База данных PostgreSQL **не упакована в приложение**, она запускается отдельно через Docker Compose.

## Требования

- Docker Desktop (Linux containers) и Docker Compose
- Для сборки: Python и зависимости из `requirements.txt`, `pyinstaller`

## Подготовка базы

1. Скопировать `.env.example` в `.env` и указать локальный пароль (не публиковать).
2. Запустить сервисы: `docker compose up -d`
3. Проверить: `docker compose ps` и `docker compose run --rm db-check`
4. При **пустой** базе импортировать скрипт (см. README, раздел про Docker Compose). Для уже заполненной базы повторный импорт без проверки недопустим.

## Сборка

Команда: `python -m PyInstaller --noconfirm --clean --onedir --name ShoeStore --add-data "resources:resources" main.py`

На Windows в `--add-data` разделитель `;` (`"resources;resources"`), результат будет `ShoeStore.exe`. Сборку нужно выполнять в той ОС, для которой предназначена программа.

## Настройка приложения

1. Скопировать `config.ini.example` в `config.ini`.
2. Указать `host = localhost`, `port = 5434`, `name = shoes_shop`, `user = shoe_user` и локальный пароль из `.env`.
3. Положить `config.ini` **рядом с запускаемым файлом** `dist/ShoeStore/ShoeStore`. Копировать нужно всю папку `dist/ShoeStore`, а не один файл.

## Запуск

`dist/ShoeStore/ShoeStore` (на Windows: `ShoeStore.exe`).

## Проверка и остановка

- Окно открывается, каталог товаров загружается, видны изображения.
- Если приложение пишет «Не удалось подключиться к базе данных»: проверить `docker compose ps`, порт и пароль в `config.ini`.
- Остановка: `docker compose stop`.
- Не использовать `docker compose down -v`: он удаляет том с данными.
