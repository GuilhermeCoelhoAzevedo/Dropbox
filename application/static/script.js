/***********************************************************************************/
/********************************General functions**********************************/
/***********************************************************************************/
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

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
        if(! document.getElementById('myFile').value){
            return false;
        };

        var par = {
            file: document.getElementById('myFile').value.replaceAll(String.fromCharCode(92),"/").trim(),
            idPath: window.location.pathname.substring(6)
        };

        console.log(par['file']);

        $.ajax({
            url: '/checkFile',
            type: 'POST',
            data: JSON.stringify(par),
            dataType: 'json',
            contentType: 'application/json',
            success: function (result, status, request) {
                $.each(result, function(i, item) {
                    if(result[0][0]){
                        //CONFIRM REPLACEMENT OF CURREN FILE
                        modalConfirmUpload(result[0][1]);
                    }else{
                        //UPLOAD FILE 
                        document.getElementById('uploadFileForm').submit();
                    }
                   
                });
            },

            error: function (event, jqxhr, settings, thrownError) {
                alert('Error to filter data. Please try again!');
            }
        });
    };
};

function create_folder(){
    if(! validateNameFolder()){
        return false;
    };
    
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

                    if(dir['id']){
                        window.location.replace(window.location.href.replace(dir['id'], item[1]));
                    } else{
                        url_dest = '/home/' + item[1];
                        window.location.assign(url_dest);
                    };
    
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

function find_duplicates(lookAll){
    var file_data = {
        idParent: window.location.pathname.substring(6),
        lookAll: lookAll
    };
    
    $.ajax({
        url: '/findDuplicates',
        type: 'POST',
        data: JSON.stringify(file_data),
        dataType: 'json',
        contentType: 'application/json',
        success: function (result, status, request) {
            duplicatesModal(result);
        },

        error: function (event, jqxhr, settings, thrownError) {
            alert('Error to filter data. Please try again!');
        }
    });
};

function share_file(){    
    if(! validateEmail()){
        return false;
    };

    idFile = '#' + $("#idFile").val();
    $(idFile).append('<input type="hidden" name="email" value="' + $("#input_info").val().toLowerCase() + '">');
    $(idFile).submit();
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

function modalConfirmUpload(file){
    initialModalValues();

    //TITLE
    $("#myModalLabel").text("Replace file");

    //BODY
    $(".modal-body").html("<p>The file <b>" + file + "</b> already exists. Would you like to replace it?</p>");

    //FOOTER
    $("#modal-action").text("Replace file");
    $("#modal-action").attr("onclick", "document.getElementById('uploadFileForm').submit();");
    
    $('#myModal').modal('show');
};

function modalShare(id){
    initialModalValues();

    //TITLE
    $("#myModalLabel").text("Share file");

    //BODY
    $(".modal-body").html("<p>Email</p>");
    $(".modal-body").append('<p><input id="input_info" name="input_info" required type="email" value=""></p>');
    $(".modal-body").append('<p id="modal-error" class="modal-error">Error</p>');
    $(".modal-body").append('<input id="idFile" type="hidden" name="email" value="' + id + '">');

    //FOOTER
    $("#modal-action").text("Share");
    $("#modal-action").attr("idFile", id);
    $("#modal-action").attr("onclick", "share_file()");
    
    $('#myModal').modal('show');
};

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
    };

    //FOOTER
    $("#modal-action").text("Confirm");
    $("#modal-action").attr("class", "btn btn-danger");
    $("#modal-action").attr("onclick", "form_action.submit()");

    $('#myModal').modal('show');
};

function duplicatesModal(result) {
    initialModalValues();

    $("#myModalLabel").text("Duplicated files: ");
    
    if(result.length > 0){
        $(".modal-body").html("")
        $.each(result, function(i, item) {
            $(".modal-body").append("<label>Duplicated files:</label><br>");
            $.each(item, function(j, file) {
                $(".modal-body").append('<p>' + file + '</p>');
            });
            $(".modal-body").append('<hr size="30" noshade>');
        });

    }else{
        $(".modal-body").css('text-align', 'center');
        $(".modal-body").html('<h2>There are no duplicated files!<h2>');
    }

    $("#modal-action").hide();
    $('#myModal').modal('show');
};

function validateNameFolder(){
    var folder  = document.getElementById('input_info').value;
    var regex   = /^[A-Za-z0-9. _-]+$/

    if (! regex.test(folder)) {
        $("#modal-error").text("Folder name not valid! Don't use specials characters (/)");
        $("#modal-error").css("display", "unset");
        
        return false;
    };

    return true;
};

function validateEmail(){
    var email = document.getElementById('input_info').value;

    if(! /^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/.test( email ) ) {
        $("#modal-error").text("Insert a valid email!");
        $("#modal-error").css("display", "unset");
        
        return false;
    };

    return true;     
};