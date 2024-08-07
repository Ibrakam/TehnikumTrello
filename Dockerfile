# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Указываем порт, который будет использоваться FastAPI
EXPOSE 8000

# Запускаем FastAPI приложение при старте контейнера
CMD ["python3", "main.py"]
