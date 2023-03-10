
Как запустить локально
---------------------------------------

```bash
$ pip3 install -r requirements.txt --no-cache-dir --no-deps   # устанавливаем библиотеки
$ uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
или в docker
```bash
$ docker-compose up -d
```
После этого веб интерфейс будет доступен по адресу http://127.0.0.1:8000/, 
вебсокет по ws://127.0.0.1:8000/ws/chat/{chatname}/.

Описание работы
---------------
- чтобы получать сообщения, нужно подключиться к сокету с указанием комнаты
- чтобы отправлять сообщения, нужно создать профиль, если профиль уже занят, то отправка сообщений работать не будет
- после закрытия сокета, созданный профиль удаляется автоматически

Протокол взаимодействия
---------------

Получение сообщений чата:
```
Server -> Client

{
  "username": "<имя пользователя>",
  "message": "<сообщение>"
}
```

Получение уведомления об ошибке:
```
Server -> Client

{
  "error": "<сообщение об ошибке>",
}
```

Создание профиля:
```
Client -> Server

{
  "command": "auth", 
  "username": "<имя пользователя>"
}
```

Отправка сообщения :
```
Client -> Server

{
  "command": "sendmessage", 
  "message": "<сообщение>"
}
```