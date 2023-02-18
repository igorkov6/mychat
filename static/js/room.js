// получить значения элементов
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const groupName = JSON.parse(document.getElementById('group-name').textContent);
const userName = JSON.parse(document.getElementById('user-name').textContent);
const firstName = JSON.parse(document.getElementById('first-name').textContent);
const lastName = JSON.parse(document.getElementById('last-name').textContent);
// const currentGroup = JSON.parse(document.getElementById('current-group').textContent);
// const contrName = JSON.parse(document.getElementById('contr-name').textContent);
const currentUser = JSON.parse(document.getElementById('current-user').textContent);

// создать сокет
const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/' + roomName + '/');

// получено сообщение от бэкэнда через сокет
chatSocket.onmessage = function (e) {

    // получить текст сообщения
    const data = JSON.parse(e.data);

    // добавить в окно чата

    let style = ' class="'
    // собственное сообщение - справа
    if (data.username === currentUser) {
        style += 'chat-right"';
        // чужое - слева
    } else {
        style += 'chat-left"'
    }

    // определить имя отправителя
    let chatName = ""
    // только для группы
    if (currentGroup) {
        // только для чужих сообщений
        if (data.username !== currentUser) {
            // определить имя
            if (data.first_name || data.last_name) {
                chatName = data.first_name + " " + data.last_name
            } else {
                chatName = data.username
            }
            chatName = '<span id="chat-name">' + chatName + '</span><br>'
        }
    }

    // получить сообщение
    let chatMessage = '<span class="chat-text"><i>' + data.message + '</i></span><br>'

    // получить текущую дату
    let today = new Date();
    let now = today.toLocaleString();
    let chatDate = '<div id="chat-time">' + now + '</div>'

    // сформировать сообщение
    if (data.message) {
        let html = '<div id="chat-box"' + style + '>' + chatName + chatMessage + chatDate + '</div>'
        document.querySelector('#chat-log').innerHTML += html;
        scrollToBottom();
    } else {
        alert('The message was empty!');
    }
};

// сокет закрыт
chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

// ввод непосредственно в окне
document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    console.log(e.keyCode)
    if (e.keyCode === 13) {  // enter, return
        send_message();
    }
};

// отправка сообщения бэкэнду - consumers.ChatConsumer.receive
send_message = function (e) {

    // получить текст сообщения
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;

    // отправить сообщение бэкэнду через сокет
    chatSocket.send(JSON.stringify({
        'message': message,
        'group': groupName,
        'username': userName,
        'first_name': firstName,
        'last_name': lastName
    }));
    // очистить окно сообщения
    messageInputDom.value = '';
};

// скролл к последнему сообщению
function scrollToBottom() {
    const objDiv = document.querySelector('#chat-log');
    objDiv.scrollTop = objDiv.scrollHeight;
}

scrollToBottom();
