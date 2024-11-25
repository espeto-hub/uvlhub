function testFakenodoConnection() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/fakenodo/api", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.status === "success") {
                    console.log("Connection successful:", response.message);
                } else {
                    console.error("Connection failed:", response.message);
                }
            } else {
                console.error("Error:", xhr.status);
            }
        }
    };
    xhr.send();
}
