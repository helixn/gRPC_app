# Импортируем необходимые библиотеки
import os
import json  # Для работы с JSON
import grpc  # Для работы с gRPC
from concurrent import futures  # Для создания пула потоков
import time  # Для работы со временем
import psycopg2  # Для работы с PostgreSQL
from psycopg2 import sql  # Для безопасного формирования SQL-запросов
import data_service_pb2  # Импортируем сгенерированные классы сообщений
import data_service_pb2_grpc  # Импортируем сгенерированные классы сервиса

# Определяем класс DataServicer, который реализует методы нашего gRPC сервиса
class DataServicer(data_service_pb2_grpc.DataServiceServicer):
    def __init__(self):
        # Устанавливаем соединение с базой данных PostgreSQL
        self.db_connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
            options="-c client_encoding=UTF8"
        )
        # Создаем таблицу в базе данных, если она еще не существует
        self.create_table()

    def create_table(self):
        # Создаем курсор для выполнения SQL-запросов
        with self.db_connection.cursor() as cursor:
            # Выполняем SQL-запрос для создания таблицы grpc_data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grpc_data (
                    PacketSeqNum INTEGER,
                    RecordSeqNum INTEGER,
                    PacketTimestamp BIGINT,
                    Decimal1 DOUBLE PRECISION,
                    Decimal2 DOUBLE PRECISION,
                    Decimal3 DOUBLE PRECISION,
                    Decimal4 DOUBLE PRECISION,
                    RecordTimestamp BIGINT,
                    PRIMARY KEY (PacketSeqNum, RecordSeqNum)
                )
            """)
        # Подтверждаем изменения в базе данных
        self.db_connection.commit()

    def SendData(self, request, context):
        try:
            # Создаем курсор для выполнения SQL-запросов
            with self.db_connection.cursor() as cursor:
                # Перебираем все записи в пакете данных
                for record_seq_num, data in enumerate(request.packet_data):
                    # Выполняем SQL-запрос для вставки данных в таблицу
                    cursor.execute(
                        sql.SQL("""
                            INSERT INTO grpc_data (
                                PacketSeqNum, RecordSeqNum, PacketTimestamp,
                                Decimal1, Decimal2, Decimal3, Decimal4, RecordTimestamp
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """),
                        (
                            request.packet_seq_num,
                            record_seq_num,
                            request.packet_timestamp,
                            data.decimal1,
                            data.decimal2,
                            data.decimal3,
                            data.decimal4,
                            data.timestamp
                        )
                    )
            # Подтверждаем изменения в базе данных
            self.db_connection.commit()
            # Возвращаем успешный ответ клиенту
            return data_service_pb2.Response(success=True, message=f"Data saved successfully. Packet: {request.packet_seq_num}, Records: {request.n_records}")
        except Exception as e:
            # В случае ошибки откатываем изменения и возвращаем сообщение об ошибке
            self.db_connection.rollback()
            return data_service_pb2.Response(success=False, message=f"Error: {str(e)}")

def serve():
    # Получаем путь к директории, в которой находится скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Формируем полный путь к файлу конфигурации
    config_path = os.path.join(script_dir, 'server_config.json')

    # Читаем конфигурацию сервера из JSON-файла
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # Создаем gRPC сервер с пулом потоков
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Добавляем наш DataServicer к серверу
    data_service_pb2_grpc.add_DataServiceServicer_to_server(DataServicer(), server)
    # Указываем адрес и порт, на котором будет работать сервер
    server.add_insecure_port(f'[::]:{config["gRPCServerPort"]}')
    # Запускаем сервер
    server.start()
    print(f"Server started on port {config['gRPCServerPort']}")
    # Ожидаем завершения работы сервера
    server.wait_for_termination()

# Если скрипт запущен напрямую (не импортирован), запускаем сервер
if __name__ == '__main__':
    serve()
