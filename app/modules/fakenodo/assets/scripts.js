function test_fakenodo_connection() {
    var response = {
        success: true, 
        messages: ["Fakenodo connection successful"], 
    };

    var simulateError = false;

    if (simulateError) {
        document.getElementById("test_fakenodo_connection_error").style.display = "block";
        response.success = false;
        response.messages = ["Fakenodo connection failed"];
    } else {
        document.getElementById("test_fakenodo_connection_error").style.display = "none";
    }
    
    console.log(response);
    console.log(response.success);
    console.log(response.messages);
}