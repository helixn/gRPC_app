# Импортируем модуль protoc из grpc_tools для генерации gRPC файлов
from grpc_tools import protoc
# Вызываем функцию main модуля protoc для генерации Python файлов из proto-файла
# Аргументы:
# '' - пустая строка (обычно здесь указывается имя скрипта)
# '-I.' - указывает искать proto-файлы в текущей директории
# '--python_out=.' - указывает генерировать Python файлы в текущей директории
# '--grpc_python_out=.' - указывает генерировать gRPC Python файлы в текущей директории
# 'data_service.proto' - имя нашего proto-файла
protoc.main((
    '',
    '-I.',
    '--python_out=.',
    '--grpc_python_out=.',
    'data_service.proto',
))

# Выводим сообщение об успешной генерации файлов
print("gRPC files generated successfully.")

# ну или 
# cmd>> python -m grpc_tools.protoc -I".\" --python_out=".\" --grpc_python_out=".\" ".\data_service.proto"