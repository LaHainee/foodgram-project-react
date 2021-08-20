# Foodgram  
[![foodgram-project-react workflow](https://github.com/VErshovBMSTU/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/VErshovBMSTU/foodgram-project-react/actions/workflows/main.yml)
## Описание
Проект Foodgram позволяет постить рецепты, делиться и скачивать списки продуктов  
## Алгоритм регистрации пользователей  
Регистрация проходит на сайте, по форме регистрации
## Запуск проекта  
#### 1. Установка Docker  
  * Установите [docker](https://docs.docker.com/engine/install/)  
  * Установите [docker-compose](https://docs.docker.com/compose/install/)  
#### 2. Запуск
  * Склонировать репозиторий  
  ```
  https://github.com/VErshovBMSTU/foodgram-project-react.git
  ```
  * Перейти в папку infra  
  ```
  cd foodgram-project-react/infra/
  ```
  * Запуск docker контейнера
  ```
  docker-compose up -d --build
  ```
  * Необходимые настройки: миграции, сбор статики, создание суперюзера
  ```
  sudo docker-compose exec backend python manage.py migrate --noinput
  sudo docker-compose exec backend python manage.py collectstatic --noinput
  sudo docker-compose exec backend python manage.py createsuperuser
  ```


