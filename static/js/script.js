var baseUrl = new URL(window.location.href);
baseUrl = `${baseUrl.protocol}//${baseUrl.hostname}:${baseUrl.port}`;
var cart_count = 0;
var productData = [];

$(document).ready(function() {
    $(".add-to-cart-btn").click(function() {
        $("#lblCartCount").html(++cart_count);
    });
});
$(document).on("change", "#modal_add_cart_content input[type='number']", function() {
    var product_id = $(this).parent().parent().attr("data-id");
    var product_quantity = $(this).val();
    var l_cart_count = 0;
    $(this).parent().parent().parent().find(".quantity").each(function() {
        l_cart_count += Number($(this).val());
    });
    cart_count = l_cart_count;
    $("#lblCartCount").html(cart_count);
});

$(document).on("click", "#modal_add_cart_content .product-close", function() {
    var product_id = $(this).parent().attr("data-id");
    var l_cart_count = $(this).parent().find(".quantity").val();

    console.log(l_cart_count, cart_count);
    cart_count -= l_cart_count;
    $("#lblCartCount").html(cart_count);
    $(this).parent().remove();
});

function add_to_cart(obj) {
    var product_id = obj.parentElement.querySelector(".product_id").value;
    var product_title = obj.parentElement.querySelector(".product-title").textContent;
    var product_price = obj.parentElement.querySelector(".product-price").textContent;
    var curr_product_quantity = obj.parentElement.querySelector(".product-quantity").value;
    curr_product_quantity = Number(curr_product_quantity) + 1;


    obj.parentElement.querySelector(".product-quantity").value = curr_product_quantity;
    

    if(($("#modal_add_cart_content").children().length == 1) || ($("#myModal_add_to_cart #modal_add_cart_content .modal-content[data-id='" + product_id + "']").length == 0) ) {
        $("#myModal_add_to_cart #modal_add_cart_content").append(
            `<div class="modal-content" class="product_id_${product_id}" data-id="${product_id}">
                <div class="product-close">
                    <span class="modal-close">&times;</span>
                </div>
                <div class="modal-header">
                    <h5 class="modal-title">${product_title}</h5>
                </div>
                <div class="modal-body">
                    <p>${product_price}</p>
                    <input type="number" name="quantity" class="quantity" value="${curr_product_quantity}">
                </div>
                <input type="hidden" name="product_id" class="product_id" value="${product_id}">
            </div>`
        );
    }
    if ( $("#myModal_add_to_cart #modal_add_cart_content .modal-content[data-id='" + product_id + "']")) {
        // update current product quantity input field
        $("#myModal_add_to_cart #modal_add_cart_content .modal-content[data-id='" + product_id + "'] .modal-body .quantity").val(curr_product_quantity);
    } 
}


$(document).on("click", "#add_to_cart", function() {
    if ($("#myModal_add_to_cart").hasClass("hide")) {
        $("#myModal_add_to_cart").removeClass("hide");
        $("#myModal_add_to_cart").addClass("show");
    }
});

$(document).on("click", "#modal_add_cart_content > .modal-close", function() {
    if ($("#myModal_add_to_cart").hasClass("show")) {
        $("#myModal_add_to_cart").removeClass("show");
        $("#myModal_add_to_cart").addClass("hide");
    }
});


$(document).on("click", "#checkout", function() {
    var checkout_data = [];
    $(".product-card").each(function() {
        if($(this).find(".product-quantity").val() > 0) {
            checkout_data.push({
                "product_id": $(this).find(".product_id").val(),
                "product_title": $(this).find(".product-title").text(),
                "product_price": $(this).find(".product-price").text(),
                "product_url": $(this).find(".product-url").attr("src"),
                "quantity": $(this).find(".product-quantity").val()
            });
        }
    });
    console.log({checkout_data});
    axios({
        method: "POST",
        url: baseUrl + "/checkout",
        data: {
            "data": checkout_data
        }
    }).then((response) => {
        console.log(response);
        document.write(response.data);
    }).catch((error) => {
        console.log(error);
    });
});

$(document).on("click", "#customer_checkout #ch_submit", function() {
    var customer_name = $(this).parent().find("#customer_name").val();
    var customer_phone = $(this).parent().find("#customer_phone").val();
    var customer_email = $(this).parent().find("#customer_email").val();
    var payment_method = $(this).parent().find("#payment_method").val();
    var state = $(this).parent().find("#state").val();
    var city = $(this).parent().find("#city").val();

    var t_products = $(".single-item");
    var products = [];

    for(let i=0; i<t_products.length; i++) {
        var temp = {}
        temp["product_name"] = t_products[i].querySelector(".product-name").value;
        var price = t_products[i].querySelector(".amount").value;
        price = price.match(/\d+/g);
        temp["product_price"] = price[0];
        temp["product_quantity"] = t_products[i].querySelector(".quantity").value;
        temp["product_id"] = t_products[i].querySelector(".product_id").value;
        products.push(temp);
    }
    
    var data = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "customer_email": customer_email,
        "payment_method": payment_method,
        "state": state,
        "city": city,
        "products": products
    }
    console.log(data);
    axios({
        method: "POST",
        url: baseUrl + "/pinvoice",
        data: {"data": data}
    }).then((response) => {
        if(response.data.success) {
            window.location.href = "/invoice";
        }
    }).catch((error) => {
        console.log(error);
    });
});

// onclick for signup button
function signup() {
    window.location.href = "/signup";
}

// onclick for login button
function farmer_login() {
    window.location.href = "/farmer_login";
}

function buyer_login() {
    window.location.href = "/buyer_login";
}

$("#signup_form #submit").click(async function(event) {
    event.preventDefault();
    var data = $("#signup_form").serializeArray();
    console.log({data});
    data = {
        "data": data
    }
    await axios({
        method: "POST",
        url: baseUrl + "/signup_farmer",
        data: data
    }).then((response) => {
        console.log(response);
        if (response.data.success) {
            if(response.data.category == "farmer") {
                window.location.href = "/login";
            } else if (response.data.category == "customer") {
                window.location.href = "/login";
            }
        } else {
            alert(response.data.message);
        }
    }).catch((error) => {
        console.log(error);
    });
})

$("#buyer_login #submit").click(async function(event) {
    event.preventDefault();
    var data = $("#buyer_login").serializeArray();
    data = {
        "data": data
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/buyer_login",
        data: data
    })
    console.log(resp);
    if(!resp.data.success) {
        alert(resp.data.message);
        $("#buyer_login").trigger("reset");
    } else {
        window.location.href = "/";
    }
});


$(document).on('click', "#login #submit", async function(event) {
    event.preventDefault();
    var data = $("#login").serializeArray();
    data = {
        "data": data
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/login",
        data: data
    });
    console.log({ resp });
    if(!resp.data.success) {
        alert(resp.data.message);
        $("#login").trigger("reset");
    } else {
        window.location.href = "/";
    }
});


$(document).on('click', "#farmer_login #submit", async function(event) {
    event.preventDefault();
    var data = $("#farmer_login").serializeArray();
    data = {
        "data": data
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/farmer_login",
        data: data
    })
    console.log(resp);
    if(!resp.data.success) {
        alert(resp.data.message);
        $("#farmer_login").trigger("reset");
    } else {
        window.location.href = "/";
    }
});

$(document).on('click', "#buyer_prof_update", async function(event) {
    event.preventDefault();
    window.location.href = "/buyer";
});

$(document).on('click', "#farmer_prof_update", async function(event) {
    event.preventDefault();
    window.location.href = "/farmer";
});

$(document).on("change", "#product_image", function() {
    console.log("Here");
    var file = this.files[0];
    var formData = new FormData();
    formData.append("file", file);
    axios({
        method: "POST",
        url: baseUrl + "/file_upload",
        data: formData
    }).then((response) => {
        console.log(response);
        if(response.data.success) {
            $("#product_image_url").val(response.data.file_url);
        }
    }).catch((error) => {
        console.log(error);
    });
});

$(document).on("change", "#category", async function(event) {
    var category = $(this).val();
    if (category != "farmer"){ 
        $(".zipcode").hide();
        return;
    }
    $(".zipcode").show();
});

$(document).on("click", "#product_add #submit", async function(event) {
    event.preventDefault();
    var data = $("#product_add").serializeArray();
    data = {
        "data": data
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/product_add",
        data: data
    });
    console.log(resp);
    if(!resp.data.success) {
        alert(resp.data.message);
        $("#product_add").trigger("reset");
    } else {
        alert(resp.data.message);
        window.location.href = "/products";
    }
});

$(document).on("click", "#product_update #submit", async function(event) {
    event.preventDefault();
    var data = $("#product_update").serializeArray();
    data = {
        "data": data
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/product_update",
        data: data
    });
    console.log(resp);
    if(!resp.data.success) {
        alert(resp.data.message);
        $("#product_update").trigger("reset");
    } else {
        alert(resp.data.message);
        window.location.href = "/profile";
    }
});

$(document).on("click", ".product-delete-btn", async function(event) {
    event.preventDefault();
    var product_id = $(this).attr("data-product_id");
    console.log(product_id);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/product_delete",
        params: {
            "product_id": product_id
        }
    });
    console.log({resp});
    if(resp.data.success) {
        alert(resp.data.message);
        window.location.href = "/products";
    } else {
        alert(resp.data.message);
    }
});

$(document).on("click", ".product-update-btn", async function(event) {
    event.preventDefault();
    var product_id = $(this).attr("data-product_id");
    console.log(product_id);
    window.location.href = "/product_update?product_id=" + product_id;
});

$(document).on('click', "form#buyer_update #submit", async function(event) {
    event.preventDefault();
    var data = $("form#buyer_update").serializeArray();
    data = {
        "data": data
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/buyer/update",
        data: data
    })
    console.log({resp});
    if(!resp.data.success) {
        alert(resp.data.message);
        $("#buyer_update").trigger("reset");
    } else {
        alert(resp.data.message);
        window.location.href = "/";
    }
});

document.getElementById('mobile-menu').addEventListener('click', function() {
    document.querySelector('.menu-items').classList.toggle('show');
});


$(document).on('click', ".chat-farmer", async function(event) {
    $(this).parent().find(".ffs-chat-panel").toggleClass("chat-visible");
});

$(document).on("click", ".chat-input .send", async function(event) {
    event.preventDefault();
    var message = $(this).parent().find(".message_text").val();
    var product_id = $(this).parent().find(".product_id").val();
    var sender = "farmer";
    var sender_id = $("#farmer_id").val();
    var receiver_id = $(this).parent().find(".customer_id").val();
    var data = {
        "message": message,
        "product_id": product_id,
        "sender_type": sender,
        "sender_id": sender_id,
        "receiver_id": receiver_id
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/chat",
        data: {"data":data}
    });
    console.log({resp});
    $(this).parent().find(".message_text").val("");
    var div_data = `
        <div class="message sent">
            ${message}
        </div>
    `;
    $(div_data).insertBefore(`#chat_id_${receiver_id} .chat-input`);
});


$(document).on('click', "#ai_side_panel #send", async function(event) {
    event.preventDefault();
    var message = $(this).parent().find(".textA textarea").val();
    var product_id = $("#ai_side_panel").attr("data-id");
    var sender = "customer";
    var sender_id = $("#buyer_id").val();
    var receiver_id = $("#ai_side_panel").attr("data-farmer_id");
    var data = {
        "message": message,
        "product_id": product_id,
        "sender_type": sender,
        "sender_id": sender_id,
        "receiver_id": receiver_id
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/chat",
        data: {"data":data}
    });
    console.log({resp});
    $(this).parent().find(".textA textarea").val("");
    var div_data = `
    <div class="message mMess">
        <div class="prof" style="background-color: #1A5D1A;">
            <p>B</p>
        </div>
        <div class="messArea">
            <p class="sname">${sender}</p>
            <div class="ai_textM bg-light shadow">${message}</div>
        </div>
    </div>
    `
    $("#ai_side_panel .chatMessages").append(div_data);
});


$(document).on("click", ".product-add-btn", function() {
    window.location.href = "/product_add";
});


$(document).on('click', ".chat-btn", async function(event) {
    var product_id = $(this).parent().find(".product_id").val();
    $(".ai_side_panel").attr("data-id", product_id);
    $(".ai_side_panel").attr("data-farmer_id", $(this).parent().find(".farmer_id").val());
    var buyer_id = $("#buyer_id").val();
    resp = await axios({
        method: "GET",
        url: baseUrl + "/chat",
        params: {
            "buyer_id": buyer_id,
            "product_id": product_id
        }
    });
    var data = resp.data;
    console.log(data);
    var chatMessages = "";
    for(let i=0; i<data.length; i++) {
        if(data[i].sender_type == "customer") {
            var div_data = `
            <div class="message mMess">
                <div class="prof" style="background-color: #1A5D1A;">
                    <p>B</p>
                </div>
                <div class="messArea">
                    <p class="sname">${data[i].sender_type}</p>
                    <div class="ai_textM bg-light shadow">${data[i].message}</div>
                </div>
            </div>
            `
            chatMessages += div_data;
        } else {
            var div_data = `
            <div class="message mMess">
                <div class="prof" style="background-color: #1A5D1A;">
                    <p>F</p>
                </div>
                <div class="messArea">
                    <p class="sname">${data[i].sender_type}</p>
                    <div class="ai_textM shadow">${data[i].message}</div>
                </div>
            </div>
            `
            chatMessages += div_data;
        }
    }
    $("#ai_side_panel .chatMessages").html(chatMessages);

    $(".ai_side_panel").toggleClass("AIpanel-visible");
});

$(document).on("click", "#ai_side_close", function() {
    $(".ai_side_panel").toggleClass("AIpanel-visible");
});

$(document).on("click", ".ffs-person", async function(event) {
    event.preventDefault();
    var farmer_id = $(this).parent().find(".farmer_id").val();
    var product_id = $(this).parent().find(".product_id").val();
    var notification_id = $(this).parent().find(".notification_id").val();

    var if_farmer = $("#farmer_id").val();
    console.log(if_farmer);
    if (if_farmer) {
        window.location.href = "/farmer_chat?notification_id=" + notification_id;
        return;
    }
    window.location.href = "/products?notification_id=" + notification_id;
});

$(document).on("click", ".weather_container #get_weather", async function(event) {
    event.preventDefault();
    var date = $(".weather_container #weather_date").val();
    console.log({date});
    resp = await axios({
        method: "POST",
        url: baseUrl + "/farmer/get_full_weather",
        params: {
            "date": date
        }
    });
    if(resp.status == 200) {
        $(".weather_container #weather_report").html(resp.data);
    } else {
        alert("Error fetching weather data");
    }
});