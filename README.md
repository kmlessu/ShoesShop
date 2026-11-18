# ShoesShop — система учёта обуви и заказов

Учебный проект демонстрационного экзамена: десктопное приложение на PySide6
с базой данных PostgreSQL для работы с каталогом обуви и заказами.

## Возможности

- авторизация пользователей, разные страницы для менеджера и администратора;
- просмотр каталога товаров с ценой, скидкой и остатком на складе;
- добавление, редактирование и удаление товаров;
- создание, изменение и удаление заказов, смена статуса заказа.

## Требования

- Python 3.13
- PostgreSQL
- библиотеки из файла requirements.txt (PySide6, psycopg2-binary)

## Установка и запуск

1. Клонировать репозиторий: `git clone https://github.com/kmlessu/ShoesShop.git`
2. Создать окружение и установить зависимости:
   `python -m venv .venv`, `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`),
   `pip install -r requirements.txt`
3. Создать базу данных `shoes_shop` и загрузить скрипт `database/shoes_shop.sql`.
4. Скопировать `config.ini.example` в `config.ini` и указать свои параметры подключения.
5. Запустить приложение: `python main.py`

## Структура репозитория

- `main.py` — точка входа
- `database.py` — работа с базой данных
- `ui/` — страницы и виджеты интерфейса
- `resources/` — изображения и логотип
- `database/` — скрипт базы данных
- `docs/` — ER-диаграмма
## Запуск PostgreSQL через Docker Compose

Требования: Docker Desktop (Linux containers).

1. Скопировать `.env.example` в `.env` и задать свой локальный пароль в `POSTGRES_PASSWORD`.
2. Запустить сервисы: `docker compose up --build -d`
3. Проверить: `docker compose ps -a` (`db` — healthy, `db-check` — Exited (0)) и `docker compose logs db-check`.
4. Импортировать базу (из скрипта убираются строки, несовместимые с PostgreSQL 14):
   `grep -v -E '^SET transaction_timeout|OWNER TO postgres|^\\(un)?restrict' database/shoes_shop.sql > /tmp/shoes_shop_clean.sql`
   `docker compose cp /tmp/shoes_shop_clean.sql db:/tmp/shoes_shop.sql`
   `docker compose exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoes_shop -f /tmp/shoes_shop.sql`
5. В `config.ini` указать `host = localhost`, `port = 5434`, `name = shoes_shop`, `user = shoe_user` и пароль из `.env`.
6. Запустить приложение: `python main.py`.
7. Остановка: `docker compose stop`. Не используйте `docker compose down -v`: тома удалят данные.

Приложение на хосте подключается к `localhost:5434`, а сервис `db-check` внутри Compose — к `db:5432`.

## Постоянное хранение и сети

- Данные PostgreSQL хранятся в именованном томе `db_data`, поэтому они сохраняются при пересоздании контейнера (`docker compose up -d --force-recreate db`).
- Резервная копия: `docker compose exec db pg_dump -U shoe_user -d shoes_shop -f /tmp/backup.sql`, затем `docker compose cp db:/tmp/backup.sql ./backups/backup.sql`. Каталог `backups/` исключён из Git.
- Восстановление: `docker compose cp ./backups/backup.sql db:/tmp/restore.sql`, затем `docker compose exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoes_shop -f /tmp/restore.sql`.
- Сервисы `db` и `db-check` работают в сети `shoe-backend`. Внутри Compose адрес базы `db:5432`, для приложения на хосте `localhost:5434` (порт опубликован только на 127.0.0.1).
- Внимание: `docker compose down -v` удаляет том и все данные. Не выполнять без резервной копии.
- 
## Сборка приложения (PyInstaller)
Инструкция по сборке и запуску в `INSTALL.md`. Конфигурация сборки сохранена в `ShoeStore.spec`. Каталоги `build/` и `dist/` в репозиторий не добавляются.
## Автор

Балаян Камилла, группа ПКС-44