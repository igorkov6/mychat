getGroups().then(() => {
})

// получить группы
async function getGroups() {
    // отправляем запрос
    const response = await fetch("/api/groups/", {
        method: "GET",
        headers: {"Accept": "application/json"}
    });

    // ответ получен
    if (response.ok === true) {
        let groups = await response.json();
        groups = groups.sort((x, y) => x.name.localeCompare(y.name));
        let htmlText = ""
        // получить группы
        groups.forEach(group => {
            htmlText += `<p><button class="list-button" onclick="groupClick(url='${group.url}', name='${group.name}')">${group.name}</button></p>`
        });
        document.getElementById("groups_column").innerHTML = htmlText;
        // очистить поля пользователей
        document.getElementById("users_column").innerHTML = "";
        document.getElementById("group_users_column").innerHTML = "";
        document.getElementById("current_group").name = "";
        document.getElementById("current_group").innerText = "";
        document.getElementById("button_group").innerText = "";
    }
}

//получить пользователей текущей группы
async function getUsers() {
    let url = document.getElementById("current_group").name;
    if (url !== "") {
        // отправляем запрос пользователей
        let response = await fetch("/api/users/", {
            method: "GET",
            headers: {"Accept": "application/json"}
        });
        // ответ получен
        if (response.ok === true) {
            // получить всех пользователей
            let users = await response.json();
            users = users.sort((x, y) => x.username.localeCompare(y.username));
            let included = ""
            let excluded = ""
            // разложить пользователей по своим окнам
            users.forEach(user => {
                // получить пользователей
                let name = user.username
                if ((user.first_name !== "") || (user.last_name !== "")) {
                    name = user.first_name + ' ' + user.last_name
                }
                // пользователь в группе
                if (user.groups.includes(url)) {
                    included += `<p><button class="list-button" onclick="userIncludedClick(url='${user.url}')">${name}</button></p>`
                    // пользователь не в группе
                } else {
                    excluded += `<p><button class="list-button" onclick="userExcludedClick(url='${user.url}')">${name}</button></p>`
                }
            });
            document.getElementById("users_column").innerHTML = excluded;
            document.getElementById("group_users_column").innerHTML = included;
        }
    }
}

// получить пользователей текущей группы
async function groupClick(url, name) {
    let elm = document.getElementById("current_group")
    elm.name = url
    elm.innerText = name
    document.getElementById("button_group").innerText = name
    await getUsers();
}

// удалить пользователя из группы
async function userIncludedClick(url) {
    console.log(url);
    // получить пользователя по url
    const response = await fetch(url, {
        method: "GET",
        headers: {"Accept": "application/json"}
    });
    // ответ получен
    if (response.ok === true) {
        let user = await response.json();
        let group_url = document.getElementById("current_group").name;
        let i = user.groups.indexOf(group_url);
        if (i !== -1) {
            user.groups.splice(i, 1);
        }
        // сохранить пользователя
        console.log(user.groups)
        let resp = await fetch(url, {
            method: "PATCH",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"groups": user.groups})
        });
        // ответ получен
        if (resp.ok === true) {
            await getUsers();
        }
    }
}

// добавить пользователя в группу
async function userExcludedClick(url) {
    // получить пользователя по url
    const response = await fetch(url, {
        method: "GET",
        headers: {"Accept": "application/json"}
    });
    // ответ получен
    if (response.ok === true) {
        let user = await response.json();
        // добавить группу в массив
        user.groups.push(document.getElementById("current_group").name)
        // сохранить пользователя
        let resp = await fetch(url, {
            method: "PATCH",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"groups": user.groups})
        });
        // ответ получен
        if (resp.ok === true) {
            await getUsers();
        }
    }
}

// удалить группу
async function deleteGroup() {
    // отправляем запрос
    let groupName = document.getElementById("current_group").name
    if (groupName !== "") {
        let response = await fetch(groupName, {
            method: "DELETE",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
        });
        // ответ получен
        if (response.ok === true) {
            await getGroups()
        }
    }
}

// создать группу
async function createGroup() {
    // получить имя группы
    let groupName = document.getElementById("group_name").value
    if (groupName !== "") {
        // отправляем запрос
        let response = await fetch("/api/groups/", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"name": groupName})
        });
        // ответ получен
        if (response.ok === true) {
            await getGroups()
        }
        document.getElementById("group_name").value = ""
    }
}

// изменить группу
async function updateGroup() {
    // получить имя группы
    let groupName = document.getElementById("current_group").name
    let newName = document.getElementById("group_name").value
    if (groupName !== "") {
        // отправляем запрос
        let response = await fetch(groupName, {
            method: "PUT",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"name": newName})
        });
        // ответ получен
        if (response.ok === true) {
            await getGroups()
        }
        document.getElementById("group_name").value = ""
    }
}
