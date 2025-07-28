https://superfoodgram.run.place/
# Foodgram - сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов.

## Ключевые возможности:
- Просмотр, создание и редактирование рецептов
- Добавление рецептов в избранное
- Добавление рецептов в список покупок с возможностью скачать этот список в формате .txt
- Получение короткой ссылки на рецепт
- Подписка на пользователя / отписка от него
- Фильтрация рецептов по тегам
- Регистрация и аутентификация пользователей

## Технологии:
#### Backend:
- Python 3.9.13
- Django 4.2.23
- Django REST Framework
- PostgreSQL
- Docker

#### Frontend:
- React
- Nginx

## Установка и запуск:

### 1. Клонируйте репозиторий:
```
git clone https://github.com/GvozdevaEkaterina/foodgram.git
cd foodgram
```

### 2. Создайте файл .env в корне проекта и укажите переменные окружения:
Пример содержания файла .env, подставьте свои значение:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,superfoodgram.run.place
```

### 3. Соберите и запустите контейнеры:
```
cd infra
docker compose up -d --build
```

### 4. Выполните миграции, создайте суперпользователя, соберите статику:
```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic --noinput
```

### 5. По желанию загрузите список ингредиентов:
```
docker compose exec backend python manage.py load_csv
```

После этого сайт будет доступен по адресу http://localhost/ или по публичному домену.

## API-документация:
Доступна по адресу /api/docs/ (Redoc)

## Автор проекта
Гвоздева Екатерина
https://github.com/GvozdevaEkaterina