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
});