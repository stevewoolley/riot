AWS.config.region = 'us-east-1'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:8c8c67e3-b02c-4815-80c2-50c09208ed08',
    Logins: {
      'cognito-idp.us-east-1.amazonaws.com/us-east-1_rm9RV1HYt': JSON.parse(localStorage.getItem('token'))
    }
});

$(document).ready(function(){
  updateAuthenticationStatus();
});

function logout(){
   localStorage.clear();
   window.location = '/';
};

function timeConverter(UNIX_timestamp){
  var a = new Date(UNIX_timestamp * 1000);
  var time = moment(UNIX_timestamp * 1000).format("YYYY/MM/DD h:mm A");
  return time;
};

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
};

function isFloat(n){
    return Number(n) === n && n % 1 !== 0;
};

function pretty_numeric(n) {
    if (isFloat(n)) {
        return n.toFixed(2);
    }
    else {
        return n;
    }
};

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
};

function updateAuthenticationStatus(){
  var user = localStorage.getItem('token');
  if(user){
    authMenuSet();
  } else {
    unauthMenuSet();
  }
};

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
    $('#settings-nav').show().append('<a href="/settings.html"><span class="glyphicon glyphicon-cog"></span> Settings</a>');
    $('#actions-nav').show().append('<a href="/actions.html">Actions</a>');
    $('#snapshots-nav').show().append('<a href="/snapshots.html">Snapshots</a>');
    $('#things-nav').show().append('<a href="/things.html">Things</a>');
    $('#logout-nav').show().append('<a onclick="logout()">Logout</a>');
}

function unauthMenuSet() {
    emptyMenuSet();
    $('#logout-nav').hide();
    $('#settings-nav').show().append('<a href="/settings.html"><span class="glyphicon glyphicon-cog"></span> Settings</a>');
    $('#actions-nav').hide();
    $('#snapshots-nav').hide();
    $('#things-nav').hide();
    $('#login-nav').show().append('<a href="/login.html">Login</a>');
}

function publish(id, title){
    var lambda = new AWS.Lambda();
    var input = {"id": id};
    lambda.invoke({
        FunctionName: 'iotPublish',
        Payload: JSON.stringify(input)
    }, function(err, data) {
        if (err) {
            console.log(err, err.stack);
            info.innerHTML = "<div class='alert alert-danger'><strong>" + err.code + "</strong></div>";
            result.innerHTML = "";
        }
        else {
            info.innerHTML = "<div class='alert alert-success'>" + title +"</div>";
        }
    });
}

$('#signin').submit(function(e){
  e.preventDefault();
  AWSCognito.config.region = 'us-east-1';
  AWSCognito.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1_rm9RV1HYt'
  });
  // Need to provide placeholder keys unless unauthorised user access is enabled for user pool
  AWSCognito.config.update({accessKeyId: 'anything', secretAccessKey: 'anything'});

  var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool({
    UserPoolId : 'us-east-1_rm9RV1HYt',
    ClientId : 'iu9gq16hq8q4ooog6slbdr6ms'
  });

  var authenticationData = {
    Username : $('#username').val(),
    Password : $('#password').val(),
  };
  var userData = {
    Username : $('#username').val(),
    Pool : userPool
  };
  var authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails(authenticationData);
  var cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

  cognitoUser.authenticateUser(authenticationDetails, {
    onSuccess: function (result) {
        localStorage.setItem('token', JSON.stringify(result.idToken.jwtToken));
        window.location = '/';
    },
    onFailure: function(err) {
        info.innerHTML = "<div class='alert alert-danger'><strong>" + err + "</strong></div>";
        unauthMenuSet();
    },
    newPasswordRequired: function(userAttributes, requiredAttributes) {
        let newPassword = prompt('A new password is required!');
        let name = prompt('Display Name');
        userAttributes.given_name = name;
        delete userAttributes.email_verified;
        delete userAttributes.phone_number_verified;
        cognitoUser.completeNewPasswordChallenge(newPassword, userAttributes, this)
    }
  });
})

$(document).ready(function() {
    // get current URL path and assign 'active' class
    var pathname = window.location.pathname;
    $('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
})
