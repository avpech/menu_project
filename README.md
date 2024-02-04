####  MenuAPI
---
REST API для меню ресторана.

---
### Стек технологий:
- Python
- FastAPI
- SQLAlchemy
- Alembic
- Docker

### Требования:
- Python версии 3.10 или выше
- PostgreSQL
- Docker
- Redis

---
##### *** ***Примечания для ревьюера***:
задание 6 (Реализовать в тестах аналог Django reverse() для FastAPI ):

Реализовано в tests/utils.py.

(альтернативно в tests/utils_alternative.py реализовал аналог этой функции с возможностью передать позиционные аргументы и повторением сигнатуры reverse() из Django. Но не стал использовать, поскольку сигнатура не такая удобная, как в utils.py, да и вроде незачем изобретать велосипед... Оставил на всякий случай)

задание 5 (дока к апи):
динамическая дока по адресу http://localhost:8000/docs (вы это и сами знаете)). Также добавил yaml со статичной докой в папку docs.

---
### Подготовка к установке

- Клонировать репозиторий и перейти в него в командной строке.
- В корне проекта создать файл .env со следующими переменными

```bash
DB_NAME=db_name
TEST_DB_NAME=db_test
DB_USER=postgresuser
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_LIFETIME=120
```
В переменных указать свои значения:
```
DB_NAME - имя базы данных
TEST_DB_NAME - имя тестовой базы данных
DB_USER - пользователь Postgres
DB_PASSWORD - пароль пользователя
DB_HOST - имя хоста (при локальном запуске указать localhost)
DB_PORT - номер порта (5432 по умолчанию)
REDIS_HOST - имя хоста redis (при локальном запуске указать localhost)
REDIS_PORT - номер порта для redis (6379 по умолчанию)
CACHE_LIFETIME - время хранения кэша
```
Имена рабочей и тестовой баз данных должны быть разными!
Пример .env файла находится в корне проекта `.env.example`

### Запуск сервиса в Docker
Для запуска сервиса ввести команду
```bash
docker-compose up -d
```
Для запуска тестов ввести команду
```bash
docker-compose -f docker-compose.test.yaml up --build --no-log-prefix --abort-on-container-exit
```
Альтернативный способ запуска контейнера с тестами
```
sh run_test.sh
```

### Локальная установка и запуск сервиса
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
source venv/bin/activate
```
```bash
python3 -m pip install --upgrade pip
```

- Установить все зависимости из файла requirements.txt

```bash
pip install -r requirements.txt
```

- Создать базы данных
```bash
psql -U postgresuser
```
```bash
CREATE DATABASE db_name;
CREATE DATABASE db_test;
```
```bash
\q
```
где `postgresuser` - пользователь Postgres, `db_name` - имя базы данных, `db_test` - имя тестовой базы данных

- Выполнить миграции

```bash
alembic upgrade head
```

- Запустить сервис

```bash
uvicorn app.main:app
```

---
Сервис будет доступен по адресу http://localhost:8000
### API сервиса
После запуска сервиса документацию к API можно увидеть по адресам:
- http://localhost:8000/docs в формате Swagger
- http://localhost:8000/redoc в формате ReDoc


##### Об авторе
Артур Печенюк
- :white_check_mark: [avpech](https://github.com/avpech)
