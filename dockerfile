# Используем Ubuntu 24.04 как базовый образ
FROM ubuntu:24.04

# Обновляем список пакетов и устанавливаем необходимые зависимости:
# - python3: интерпретатор Python
# - python3-pip: менеджер пакетов для Python
# - postgresql: система управления базами данных
# - postgresql-contrib: дополнительные модули для PostgreSQL
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv\
    postgresql \
    postgresql-contrib

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt в текущую директорию контейнера
COPY requirements.txt .

# Устанавливаем Python-зависимости из файла requirements.txt
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем все файлы из текущей директории хоста в рабочую директорию контейнера
COPY . .

# Запускаем PostgreSQL, создаем базу данных 'grpc_db'(postgres), затем останавливаем сервис.
# Это нужно для инициализации базы данных при сборке образа.
RUN service postgresql start && \
    su - postgres -c "psql -c 'CREATE DATABASE grpc_db;'" && \
    service postgresql stop

# Открываем порт 50051 для gRPC сервера
EXPOSE 50051

# Команда, выполняемая при запуске контейнера:
# 1. Запускаем сервис PostgreSQL
# 2. Запускаем Python-скрипт server.py
CMD ["bash", "-c", "service postgresql start && . venv/bin/activate && python3 server.py"]
