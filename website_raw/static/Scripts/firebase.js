$(function() {
    // Your web app's Firebase configuration
    var firebaseConfig = {
        apiKey: "AIzaSyAox87exyw3TRIQ7FdiiafCGgWkck1BscU",
        authDomain: "buddhi-35a82.firebaseapp.com",
        databaseURL: "https://buddhi-35a82.firebaseio.com",
        projectId: "buddhi-35a82",
        storageBucket: "buddhi-35a82.appspot.com",
        messagingSenderId: "171748301229",
        appId: "1:171748301229:web:ceb34b2a65089c98f6e924",
        measurementId: "G-ZD68CMQSLQ"
    };
    // Initialize Firebase
    firebase.initializeApp(firebaseConfig);

    var uiConfig = {
        signInSuccessUrl: 'loggedin.html',
        signInOptions: [
            // Leave the lines as is for the providers you want to offer your users.
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            // firebase.auth.FacebookAuthProvider.PROVIDER_ID,
            // firebase.auth.TwitterAuthProvider.PROVIDER_ID,
            // firebase.auth.GithubAuthProvider.PROVIDER_ID,
            firebase.auth.EmailAuthProvider.PROVIDER_ID,
            //firebase.auth.PhoneAuthProvider.PROVIDER_ID,
            //firebaseui.auth.AnonymousAuthProvider.PROVIDER_ID
        ],
        // tosUrl and privacyPolicyUrl accept either url string or a callback
        // function.
        // Terms of service url/callback.
        tosUrl: 'index.html',
        // Privacy policy url/callback.
        privacyPolicyUrl: function() {
            window.location.assign('index.html');
        },
        signInFlow: "popup"
    };

    // Initialize the FirebaseUI Widget using Firebase.
    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    // The start method will wait until the DOM is loaded.
    ui.start('#firebaseui-auth-container', uiConfig);

});

function logout() {
    // window.alert("Works")
    firebase.auth().signOut().then(function() {
        // Sign-out successful.
        location = "/website_raw/login.html"
    }).catch(function(error) {
        // An error happened.
    });
}