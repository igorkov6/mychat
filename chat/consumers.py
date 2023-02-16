# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message
from django.contrib.auth.models import User, Group
from loguru import logger
import datetime
import bleach
from .views import rds

expire_time = 3600


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Управление рассылкой сообщений, полученных от пользователя
    всем участникам группы
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_name = None

    async def connect(self):
        """
        Открыть сокет для текущего пользователя и добавить в группу
        :return:
        """
        # определить имя группы
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # добавить сокет в группу
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Закрыть сокет и удалить из группы
        :param close_code:
        :return:
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Получено сообщение от фронтэнда через сокет
        :param text_data: данные от room.html.js.send_message в формате json
        :return:
        """
        # получить сообщение
        text_data_json = json.loads(text_data)
        message = bleach.clean(text_data_json["message"])
        group_name = text_data_json["group"]
        username = text_data_json["username"]
        first_name = text_data_json["first_name"]
        last_name = text_data_json["last_name"]
        date_added = datetime.datetime.now()

        # сохранить сообщение в базе
        await self.save_message(group_name, username, message)

        # сохранить сообщение в стеке
        await self.push_record(group_name, username, message)

        # разослать сообщение сокетам группы через chat_message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "group": group_name,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "date_added": date_added,
            }
        )

    async def chat_message(self, event):
        """
        Рассылка сообщения фронтэндам
        :param event:
        :return:
        """
        # получить сообщение
        message = event["message"]
        group = event["group"]
        username = event["username"]
        first_name = event["first_name"]
        last_name = event["last_name"]

        # отправить сообщение фронтэндам через сокет
        await self.send(text_data=json.dumps(
            {
                "message": message,
                "group": group,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        ))

    @sync_to_async
    def save_message(self, group, username, message):
        """
        сохранить сообщение в базе данных
        :param group:
        :param username:
        :param message:
        :return:
        """
        user = User.objects.get(username=username)
        group = Group.objects.get(name=group)
        Message.objects.create(user=user, group=group, content=message)

    @sync_to_async
    def push_record(self, group_name, username, message):

        # получить пользователя
        current_user = User.objects.get(username=username)
        # получить группу
        group = Group.objects.get(name=group_name)

        # пара
        if str(group_name).startswith("group_"):
            ids = str(group_name).split("_")
            ids.remove("group")
            # отправить собеседнику
            for user_id in ids:
                # себе не отправлять
                if int(user_id) != int(current_user.id):
                    sender = "user:{}".format(current_user.id)
                    target = "user:{}".format(user_id)
                    record = json.dumps({"sender": sender, "message": message[:20]})
                    rds.lpush(target, record)
                    rds.expire(target, expire_time)

        # группа
        else:
            users = User.objects.filter(groups=group)
            # отправить каждому в группе
            for user in users:
                # себе не отправлять
                if user != current_user:
                    sender = "group:{}".format(group.id)
                    target = "user:{}".format(user.id)
                    record = json.dumps({"sender": sender, "message": message})
                    rds.lpush(target, record)
                    rds.expire(target, expire_time)
