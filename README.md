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
### Подготовка к установке

- Клонировать репозиторий и перейти в него в командной строке.
- В корне проекта создать файл .env в соответствии с  `.env.example`

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
