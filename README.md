# hw05_final

Социальная сеть для публикации записей. Сервис позволяет зарегистрироваться, создать запись, которая принадлежит определенной группе, редактировать и комментировать её.
## Использованные технологии: 
* Python 3
* Django
* Pytest
* Bootstrap
## Установка проекта на рабочую машину

Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:Sausetardar/hw05_final.git
```
```
cd hw05_final
```

Создать и активировать виртуальное окружение:

```
py  -m venv venv
```

```
source venv\Scripts\activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
