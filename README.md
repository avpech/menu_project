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
- RabbitMQ

---
##### *** ***Примечания для ревьюера***:
- Задание 2. Добавить в проект фоновую задачу с помощью Celery + RabbitMQ (локальный файл)
Для использования локальной таблицы указать в .env USE_GOOGLE_SHEETS=False. Реализовано в пакете app.tasks (там просто ужас). Валидацияя значений ячеек таблицы спомощью pydantic-схем из app.schemas.table.py.
Алгоритмическая сложность сравнения табличных данных и данных из базы получилась квадратичной. Можно было сделать линейной с помощью словарей, но решил не усложнять и без того кошмарный код.
- Задание 3. Добавить эндпоинт (GET) для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами.
Вью нового эндпоинта app.api.endpoints.menu.get_all_nested.
orm-запрос в app.crud.menu.CRUDMenu.get_all. На мой взгляд было проще и удобней воспользоваться joinload, но в задании явно было указано использовать подзапросы и агрегирующие функции, поэтому использовал подзапросы и агрегирующие функции postgres, формируя списки/словари на стороне бд (мне не понравилось))
- Задание 4. Реализовать инвалидация кэша в background task (встроено в FastAPI)
task-и в сервисном слое в app.services
- Задание 5.  Обновление меню из google sheets раз в 15 сек.
Указать в .env USE_GOOGLE_SHEETS=True, в GOOGLE_SHEET_ID указать id гугл-таблицы. Туда же данные сервисного аккаунта гугл (пример в env.example)
- Задание 6. Блюда по акции. Размер скидки (%) указывается в столбце G файла.
В чате была инфа. что нельзя хранить размер скидки в базе, поэтому хранил ее в кеше. Цена со скидкой выводится только для GET-запросов. Во время фоновой задачи записывается в кеш (в последней функции app.tasks.utils.py). В crud слое забирается из кеша.


---
### Подготовка к установке

- Клонировать репозиторий и перейти в него в командной строке.
- В корне проекта создать файл .env в соответсвии с  `.env.example`

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
- Установить и активировать виртуальное окружение c учетом версии Python 3.10 или выше, обновить менеджер пакетов pip:

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

- Запустить celery

```bash
celery -A app.tasks.celery_tasks:celery_app worker --beat --loglevel=info
```
(для Windows дополнитеьно добавить аргумент --pool=solo)

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
