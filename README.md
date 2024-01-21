####  MenuAPI
---
REST API для меню ресторана.

---
### Стек технологий:
- Python
- FastAPI
- SQLAlchemy
- Alembic

### Требования:
- Python версии 3.9 или выше
- PostgreSQL

### Локальная установка и запуск сервиса
- Клонировать репозиторий и перейти в него в командной строке.
- Установить и активировать виртуальное окружение c учетом версии Python 3.9 или выше, обновить менеджер пакетов pip:

Git Bash
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
```bash
python -m pip install --upgrade pip
```
Linux
```bash
python3 -m venv venv
```
```bash
source env/bin/activate
```
```bash
python3 -m pip install --upgrade pip
```

- Установить все зависимости из файла requirements.txt

```bash
pip install -r requirements.txt
```

- В корне проекта создать файл .env со следующими переменными

```bash
DB_NAME=db_name
DB_USER=postgresuser
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```
В переменных указать свои значения:
```
DB_NAME - имя базы данных
DB_USER - пользователь Postgres
DB_PASSWORD - пароль пользователя
DB_HOST - имя хоста (при локальном запуске указать localhost)
DB_PORT - номер порта (5432 по умолчанию)
```
Пример .env файла находится в корне проекта `.env.example`
- При необходимости создать базу данных
```bash
psql -U postgresuser
```
```bash
CREATE DATABASE db_name;
\q
```
где `postgresuser` - пользователь Postgres, `db_name` - имя базы данных

- Выполнить миграции

```bash
alembic upgrade head
```

- Запустить сервис

```bash
uvicorn app.main:app
```
Сервис будет доступен по адресу http://localhost:8000
### API сервиса
После запуска сервиса документацию к API можно увидеть по адресам:
- http://localhost:8000/docs в формате Swagger
- http://localhost:8000/redoc в формате ReDoc


##### Об авторе
Артур Печенюк
- :white_check_mark: [avpech](https://github.com/avpech)