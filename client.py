# Импортируем необходимые библиотеки
import os
import json  # Для работы с JSON
import grpc  # Для работы с gRPC
import time  # Для работы со временем и задержками
import random  # Для генерации случайных чисел
import data_service_pb2  # Импортируем сгенерированные классы сообщений
import data_service_pb2_grpc  # Импортируем сгенерированные классы клиента

def generate_data():
    # Функция для генерации случайных данных
    return data_service_pb2.Data(
        decimal1=random.uniform(0, 100),  # Генерируем случайное число от 0 до 100
        decimal2=random.uniform(0, 100),
        decimal3=random.uniform(0, 100),
        decimal4=random.uniform(0, 100),
        timestamp=int(time.time() * 1000)  # Текущее время в миллисекундах
    )

def run():
    # Получаем путь к директории, в которой находится скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Формируем полный путь к файлу конфигурации
    config_path = os.path.join(script_dir, 'client_config.json')
    # Читаем конфигурацию клиента из JSON-файла

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # Создаем канал связи с сервером
    channel = grpc.insecure_channel(f"{config['gRPCServerAddr']}:{config['gRPCServerPort']}")
    # Создаем клиентский stub для взаимодействия с сервером
    stub = data_service_pb2_grpc.DataServiceStub(channel)

    # Отправляем заданное количество пакетов
    for packet_seq_num in range(config['TotalPackets']):
        # Генерируем данные для пакета
        packet_data = [generate_data() for _ in range(config['RecordsInPacket'])]
        packet_timestamp = int(time.time() * 1000)  # Текущее время в миллисекундах
        
        # Создаем пакет данных
        packet = data_service_pb2.DataPacket(
            packet_timestamp=packet_timestamp,
            packet_seq_num=packet_seq_num,
            n_records=len(packet_data),
            packet_data=packet_data
        )

        try:
            # Отправляем пакет на сервер и получаем ответ
            response = stub.SendData(packet)
            print(f"Packet {packet_seq_num} sent. Server response: {response.message}")
        except grpc.RpcError as e:
            # В случае ошибки выводим сообщение
            print(f"Error sending packet {packet_seq_num}: {e}")

        # Ждем заданное время перед отправкой следующего пакета
        time.sleep(config['TimeInterval'])

    print("All packets sent. Client shutting down.")

# Если скрипт запущен напрямую (не импортирован), запускаем клиент
if __name__ == '__main__':
    run()
