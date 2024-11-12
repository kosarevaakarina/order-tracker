# Сервис заказов

## Технологии

* Python
* FaspAPI
* Apache Kafka
* PostgreSQL
* Prometheus + Grafana
* Docker

## Сущности

- Product (продукты)
- Order (заказы)

## Настройка сервиса
_Для запуска проекта необходимо клонировать репозиторий и создать файл .env согласно .env.example:_
```
# Database

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=tracker

#OAuth2
SECRET_KEY = 'secret-key'

#SMPT
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-mail@gmail.com"
SMTP_PASSWORD = "your-password"

#Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CONSUMER_GROUP=group-id

PYTHONPATH=/app/src
```

_Запустить docker-compose:_

```
docker-compose up --build
```


