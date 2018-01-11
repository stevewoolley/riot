AWS.config.region = 'us-east-1'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:8c8c67e3-b02c-4815-80c2-50c09208ed08',
    Logins: {
        'cognito-idp.us-east-1.amazonaws.com/us-east-1_rm9RV1HYt': JSON.parse(localStorage.getItem('token'))
    }
});

$(document).ready(function () {
    updateAuthenticationStatus();
});

function logout() {
    localStorage.clear();
    window.location = 'login.html';
}

function timeConverter(UNIX_timestamp) {
    return moment(UNIX_timestamp * 1000).format("YYYY/MM/DD h:mm A");
}

function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function isFloat(n) {
    return Number(n) === n && n % 1 !== 0;
}

function pretty_numeric(n) {
    if (isFloat(n)) {
        return n.toFixed(2);
    }
    else {
        return n;
    }
}

function alert_msg(style, msg) {
    return "<div class='alert alert-" + style + "' role='alert'>" + msg + "</div>";
}

function getParameterByName(name, url) {
    if (!url) {
        url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

sizeOf = function (bytes) {
    if (bytes == 0) {
        return "0.00 B";
    }
    var e = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, e)).toFixed(2) + ' ' + ' KMGTP'.charAt(e) + 'B';
}

function updateAuthenticationStatus(user) {
    var user = localStorage.getItem('token');
    if (user) {
        authMenuSet();
    } else {
        unauthMenuSet();
    }
    // hilite active menu item
    var pathname = window.location.pathname.split('/');
    $('.navbar a[href="' + pathname[pathname.length -1] + '"]').parent().addClass('active');
}

var info = document.getElementById('info');
var result = document.getElementById('result');

function emptyMenuSet() {
    $('#login-nav').empty();
    $('#logout-nav').empty();
    $('#settings-nav').empty();
    $('#actions-nav').empty();
    $('#snapshots-nav').empty();
    $('#things-nav').empty();
}

function authMenuSet() {
    emptyMenuSet();
    $('#login-nav').hide();
    $('#settings-nav').show().append('<a class="nav-link" title="Settings" href="settings.html"><i class="fa fa-user"></i></a>');
    $('#actions-nav').show().append('<a class="nav-link" href="actions.html">Actions</a>');
    $('#snapshots-nav').show().append('<a class="nav-link" href="snapshots.html">Snapshots</a>');
    $('#things-nav').show().append('<a class="nav-link" href="things.html">Things</a>');
    $('#logout-nav').show().append('<a class="nav-link" title="Logout" onclick="logout()"><i class="fa fa-lock"></a>');
}

function unauthMenuSet() {
    emptyMenuSet();
    $('#logout-nav').hide();
    $('#settings-nav').hide();
    $('#actions-nav').hide();
    $('#snapshots-nav').hide();
    $('#things-nav').hide();
    $('#login-nav').show().append('<a class="nav-link" title="Login" href="login.html"><i class="fa fa-unlock"></a>');
}

function publish(key, title) {
    var lambda = new AWS.Lambda();
    var input = {"key": key};
    lambda.invoke({
        FunctionName: 'iotPublish',
        Payload: JSON.stringify(input)
    }, function (err, data) {
        if (err) {
            console.log(err, err.stack);
            info.innerHTML = alert_msg('danger', err.code);
            result.innerHTML = "";
        }
        else {
            info.innerHTML = alert_msg('success', title);
        }
    });
}

$('#signin').submit(function (e) {
    e.preventDefault();
    AWSCognito.config.region = 'us-east-1';
    AWSCognito.config.credentials = new AWS.CognitoIdentityCredentials({
        IdentityPoolId: 'us-east-1_rm9RV1HYt'
    });

    // Need to provide placeholder keys unless unauthorised user access is enabled for user pool
    AWSCognito.config.update({accessKeyId: 'anything', secretAccessKey: 'anything'});

    var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool({
        UserPoolId: 'us-east-1_rm9RV1HYt',
        ClientId: 'iu9gq16hq8q4ooog6slbdr6ms'
    });

    var authenticationData = {
        Username: $('#username').val(),
        Password: $('#password').val()
    };

    var userData = {
        Username: $('#username').val(),
        Pool: userPool
    };

    var authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails(authenticationData);
    var cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function (result) {
            localStorage.setItem('token', JSON.stringify(result.idToken.jwtToken));
            localStorage.setItem('username', userPool.getCurrentUser().username);
            window.location = 'index.html';
        },
        onFailure: function (err) {
            info.innerHTML = alert_msg('danger', err);
            unauthMenuSet();
        },
        newPasswordRequired: function (userAttributes, requiredAttributes) {
            var newPassword = prompt('A new password is required!');
            userAttributes.given_name = prompt('Display Name');
            delete userAttributes.email_verified;
            delete userAttributes.phone_number_verified;
            cognitoUser.completeNewPasswordChallenge(newPassword, userAttributes, this)
        }
    });
});
