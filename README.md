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
- Python версии 3.9 или выше
- PostgreSQL
- Docker

---
##### *** ***Примечания для ревьюера***:

1) Администратор чата в телеграм сказал указать в ридми путь к методу, где рализован 3-й пункт задания. Указываю: `app.crud.menu.CRUDmenu.get_multy` для списка меню, и `app.crud.menu.CRUDmenu.get` для отдельного меню
2) Ручкы покрывал тестами, так сказать, "по-науке" - то есть взаимно независимыми и по возможности атомарными. Пусть отрабатывают они медленней из-за необходимости подчищать бд за собой, но зато есть уверенность, что при внесении изменений в один тест не сломаются остальные. Но когда дошел до выполнения задания 4 (Реализовать тестовый сценарий «Проверка кол-ва блюд и подменю в меню» из Postman), столкнулся с тем, что из-за некоторых особенностей формирования `event loop`-ов в `pytest-asyncio` реализовать одновременно с ними взаимно зависмые тесты весьма проблематично. Поэтому вместо буквального воспроизведения всех тестов сценария из Postman реализовал покрытие всех проверок сценария спомощью взаимно независимых тестов, воспроизведя в них логику из сценария (проще говоря, для подготовки данных в бд использовал фикстуры вместо запросов к эндпоинтам) Реализация пункта задания 4 находится в `tests.test_2_scenario.py` 
---
### Подготовка к к установке

- Клонировать репозиторий и перейти в него в командной строке.
- В корне проекта создать файл .env со следующими переменными

```bash
DB_NAME=db_name
TEST_DB_NAME=db_test
DB_USER=postgresuser
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```
В переменных указать свои значения:
```
DB_NAME - имя базы данных
TEST_DB_NAME - имя тестовой базы данных
DB_USER - пользователь Postgres
DB_PASSWORD - пароль пользователя
DB_HOST - имя хоста (при локальном запуске указать localhost)
DB_PORT - номер порта (5432 по умолчанию)
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