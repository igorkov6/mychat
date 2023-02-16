# chat/views.py
from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User, Group
from loguru import logger
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Message, Profile
from django.contrib import messages
import redis, json
from django.conf import settings


"""
создать соединение с redis
"""
try:
    rds = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
except Exception:
    pass


def dashboard(request):
    """
    стартовая страница
    :param request:
    :return:
    """
    return render(request, 'dashboard.html', {'section': dashboard})


@login_required
def chat(request):
    """
    форма выбора чата
    :param request:
    :return:
    """
    # получить данные для формы

    # текущий пользователь
    current_user = request.user

    # группы для текущего пользователя
    groups = Group.objects.filter(user=request.user.id)

    # зарегистрированные пользователи кроме текущего
    users = User.objects.all().exclude(id=current_user.id).order_by('username')

    # открыть форму
    return render(request, "chat/chat.html", {'current_user': current_user,
                                              'groups': groups,
                                              'users': users,
                                              'section': 'chat',
                                              'current_group': '',
                                              'contr_name': ''})


@login_required
def room(request, room_name):
    """
    форма room
    :param request:
    :param room_name: имя группы формируется на странице chat.html следующим образом:
                        для группы - group_n - где n - id существующей группы в db
                        для пары пользователей - group_x_y - где x и y - id пользователей,
                        так, что x < y. Если такая группа не существует в db - она будет создана
    :return:
    """

    # получить имя группы
    group_name = str(room_name)
    current_group = ""

    # group_x - существующая группа - получить имя
    group_ids = str(room_name).split('_')
    if len(group_ids) == 2:
        group_name = Group.objects.get(id=group_ids[1]).name
        current_group = group_name

    # group_x_y - пара пользователей
    else:
        # если группа пары не существует - создать
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)

    # получить сообщения группы
    reports = Message.objects.filter(group=Group.objects.get(name=group_name))

    # получить имя текущего пользователя
    current_user = request.user.username

    # имя контр пользователя
    contr_name = ""

    # если пара
    photo = None
    if len(group_ids) == 3:
        current_group = ""
        # получить контр пользователя
        contr_id = group_ids[1] if int(request.user.id) == int(group_ids[2]) else group_ids[2]
        contr_user = User.objects.get(id=contr_id)
        # получить имя контр пользователя
        if contr_user.first_name or contr_user.last_name:
            contr_name = f'{contr_user.first_name} {contr_user.last_name}'
        else:
            contr_name = contr_user.username
        # получить фото контр пользователя
        try:
            photo = contr_user.profile.photo
        except Exception:
            pass

    # передать параметры форме
    return render(request, "chat/room.html", {
        'room_name': room_name,           # имя комнаты для открытия сокета Websock ( group_n / group_x_y )
        'current_group': current_group,   # name группы. Только для чата в группе. ( name )
        'group_name': group_name,         # name группы в базе данных для любого чата. ( name / group_x_y )
        'current_user': current_user,     # username текущего пользователя.
        'contr_name': contr_name,         # Полное имя контр пользователя. Только для чата в паре.
        'reports': reports,               # сообщения чата из базы данных.
        'photo': photo,                   # фото контр пользователя если есть
        'section': 'room',                # название секции
    })


@login_required
def edit(request):
    """
    форма редактора профиля текущего пользователя
    :param request:
    :return:
    """

    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST, files=request.FILES)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваши личные данные изменены.')
            return render(request, 'dashboard.html')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'registration/edit.html', {'user_form': user_form, 'profile_form': profile_form})


def register(request):
    """
    форма регистрации пользователя
    :param request:
    :return:
    """
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})


@login_required
def group(request):
    """
    форма управления групповыми чатами
    :param request:
    :return:
    """
    return render(request, 'chat/group.html', {'section': 'group',
                                               'current_group': '',
                                               'contr_name': ''})


@login_required
def update(request):
    """
    Получить сообщение из стека
    :param request:
    :return:
    """

    # получатель
    name = "user:{}".format(request.user.id)
    # найти сообщение для получателя
    record = rds.rpop(name)
    # сообщение есть
    if record is not None:
        my_dict = json.loads(record)

        # получить данные из словаря
        sender = my_dict["sender"]
        message = my_dict["message"]

        # найти имя отправителя
        sender = sender.split(":")
        if sender[0] == "user":
            user = User.objects.get(id=sender[1])
            if user.first_name or user.last_name:
                sender = user.first_name + " " + user.last_name
            else:
                sender = user.username
        else:
            sender = Group.objects.get(id=sender[1]).name

        # возвратить json в ответе
        return HttpResponse(json.dumps({"sender": sender, "message": message}), status=200)

    # сообщения нет - отправить пустое сообщение
    return HttpResponse(json.dumps({"sender": "", "message": ""}), status=200)
