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

function createFakenodoDeposition() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/fakenodo/api", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 201) {
                var response = JSON.parse(xhr.responseText);
                console.log("Deposition created:", response.message);
            } else {
                console.error("Failed to create deposition. Status:", xhr.status);
            }
        }
    };
    xhr.send();
}

function uploadDepositionFile(depositionId) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", `/fakenodo/api/${depositionId}/files`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 201) {
                var response = JSON.parse(xhr.responseText);
                console.log("File uploaded:", response.message);
            } else {
                console.error("File upload failed. Status:", xhr.status);
            }
        }
    };
    xhr.send();
}

function deleteDeposition(depositionId) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", `/fakenodo/api/${depositionId}`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log("Deposition deleted:", response.message);
            } else {
                console.error("Failed to delete deposition. Status:", xhr.status);
            }
        }
    };
    xhr.send();
}

function publishDeposition(depositionId) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", `/fakenodo/api/${depositionId}/actions/publish`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 202) {
                var response = JSON.parse(xhr.responseText);
                console.log("Deposition published:", response.message);
            } else {
                console.error("Failed to publish deposition. Status:", xhr.status);
            }
        }
    };
    xhr.send();
}

function getDeposition(depositionId) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", `/fakenodo/api/${depositionId}`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log("Deposition retrieved:", response.message, "DOI:", response.doi);
            } else {
                console.error("Failed to retrieve deposition. Status:", xhr.status);
            }
        }
    };
    xhr.send();
}
