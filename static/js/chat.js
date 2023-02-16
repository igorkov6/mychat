// получить id текущего пользователя
const currentId = JSON.parse(document.getElementById('json-current').textContent);
console.log(currentId)

// обработать нажатие группы
function group_click(id) {
    let roomName = 'group_' + id
    console.log(roomName)
    window.location.pathname = '/room/' + roomName + '/';
}

// обработать нажатие пользователя
function user_click(contrId) {
    let roomName = 'group_'
    Number(contrId) < Number(currentId) ? roomName += contrId + '_' + currentId : roomName += currentId + '_' + contrId
    window.location.pathname = '/room/' + roomName + '/';
}