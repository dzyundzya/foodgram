# "Продуктовый помощник" (Foodgram)
---
## 1. Описание и установка проекта

 «Фудграм» — сайт, на котором пользователь может публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

```
git clone git@github.com:dzyundzya/foodgram.git
```

***- Установите и активируйте виртуальное окружение:***
- для MacOS
```
python3 -m venv venv
```
- для Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```

***- Установите зависимости из файла requirements.txt:***
```
pip install -r requirements.txt
```

***- Примените миграции:***
```
python manage.py migrate
```

***- В папке с файлом manage.py выполните команду для запуска локально:***
```
python manage.py runserver

```
## 2. База данных и переменные окружения

Проект использует базу данных PostgreSQL.  
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env".

```
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_USER` - пользователь базы данных
- `POSTGRES_PASSWORD` - пароль
- `DB_HOST` - имя хоста базы данных
- `DB_PORT` - порт базы данных 5432
- `SECRET_KEY` - секретный ключ Джанго
- `DEBUG` - логическое значение True or False 
- `ALLOWED_HOSTS` - домен, localhost 127.0.0.1
- `DB_ENGINE` - PostgreSQL

```
Учетная запись администратора:
- почта: yo@yo.yo
- пароль: yo
ip и домен сайта:
<<<<<<< HEAD
- 130.193.42.2, dzyundzya-foodgram.ddns.net
=======
- 130.193.42.2, https://dzyundzya-foodgram.ddns.net/
>>>>>>> 6bd2fbebd06472e73cd4d377cebb3fab9b24a1b6
---
## 3. Техническая информация 

Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.
