/***********************************************************************************/
/********************************General functions**********************************/
/***********************************************************************************/
if(document.getElementById('sign-out')) {
    document.getElementById('sign-out').onclick = function() {
        // ask firebase to sign out the user
        firebase.auth().signOut();
    };
};

setTimeout(function() {
    $('#flashMessage').fadeOut('fast');
}, 4000); 

if(document.getElementById('myFile')) {
    document.getElementById('myFile').onchange = function() {
        document.getElementById('uploadFileForm').submit()
        document.getElementById('myFile').value = "";
    };
};

function create_folder(){
    if(! validateNameFolder()){
        return false;
    }
    
    var dir = {
        folder: document.getElementById('input_info').value.trim() + "/",
        id: window.location.pathname.substring(6)
    };

    $.ajax({
        url: '/createFolder',
        type: 'POST',
        data: JSON.stringify(dir),
        dataType: 'json',
        contentType: 'application/json',
        success: function (result, status, request) {
            $.each(result, function(i, item) {
                if(item[0] == 0){
                    document.getElementById('modal-cancel').click();
                    window.location.replace(window.location.href.replace(dir['id'], item[1]));
                }else{
                    location.reload();
                }
            });
        },

        error: function (event, jqxhr, settings, thrownError) {
            alert('Error to filter data. Please try again!');
        }
    });
    
    document.getElementById('modal-cancel').click();
};
/***********************************************************************************/
/********************************Firebase functions*********************************/
/***********************************************************************************/
var uiConfig = {
    signInSuccessUrl: '/login',
    signInOptions: [
    firebase.auth.GoogleAuthProvider.PROVIDER_ID,
    firebase.auth.EmailAuthProvider.PROVIDER_ID
    ]
};

firebase.auth().setPersistence(firebase.auth.Auth.Persistence.SESSION).then(() => {
    initializeAuth();
});

function initializeAuth(){
    firebase.auth().onAuthStateChanged(function(user) {
        if(user) {
            //CREATE COOKIE WITH THE USER DATA
            user.getIdToken().then(function(token) {
                document.cookie = "token=" + token + ";domain=;path=/";
            });
        } else {
            //CREATE LOGIN CONTAINER
            if(document.getElementById('firebase-auth-container')) {
                var ui = new firebaseui.auth.AuthUI(firebase.auth());
                ui.start('#firebase-auth-container', uiConfig);
            }
            document.cookie = "token=" + ";domain=;path=/";
        }
        }, function(error) {
            alert('Unable to log in: ' + error);
        }
    );
};
/***********************************************************************************/
/********************************MODAL FORM functions*******************************/
/***********************************************************************************/
$(document).ready(function(e) {
    $('#myModal').modal({
        backdrop: 'static',
        keyboard: true,
        show: false,
    });

    $('#myModal').on('shown.bs.modal', function () {
        $('#input_info').focus();
    })  

    $(document).on("click", "#btn-NewFolder", function() {    
        initialModalValues();
        
        //TITLE
        $("#myModalLabel").text("Create Folder");

        //BODY
        $(".modal-body").html("<label>Name</label>");
        $(".modal-body").append('<p><input id="input_info" name="input_info" required type="text" value=""></p>');
        $(".modal-body").append('<p id="modal-error" class="modal-error">Error</p>');
        
        //FOOTER
        $("#modal-action").text("Create");
        $("#modal-action").attr("onclick", "create_folder()");
        
        $('#myModal').modal('show');
    });
});

function validateNameFolder(){
    var folder  = document.getElementById('input_info').value;
    var regex   = /^[A-Za-z0-9. _-]+$/

    if (! regex.test(folder)) {
        $("#modal-error").text("Folder name not valid! Don't use specials characters (/)");
        $("#modal-error").css("display", "unset");
        
        return false;
    }

    return true;
}

function initialModalValues(){
    $("#modal-action").show();
    $("#modal-action").attr("class", "btn btn-dark");
    $("#modal-action").text("Save changes");
    $(".modal-body").css('text-align', 'initial');
};

var form_action;

function confirmDelete(form){
    initialModalValues();
    form_action = form;

    if(form_action.name == 'deleteFile'){
        //TITLE
        $("#myModalLabel").text("Delete file?");
        //BODY
        $(".modal-body").html("<p>Are you sure do you want to delete this file?</p>");
    }else{
        //TITLE
        $("#myModalLabel").text("Delete folder?");
        //BODY
        $(".modal-body").html("<p>Are you sure do you want to delete this folder?</p>");
    }

    //FOOTER
    $("#modal-action").text("Confirm");
    $("#modal-action").attr("class", "btn btn-danger");
    $("#modal-action").attr("onclick", "form_action.submit()");

    $('#myModal').modal('show');
}