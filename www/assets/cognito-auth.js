var Snerted = window.Snerted || {};

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

function alert_msg(style, msg) {
    return "<div class='alert alert-" + style + "' role='alert'>" + msg + "</div>";
}

(function scopeWrapper($) {
    var signinUrl = 'login.html';

    var poolData = {
        UserPoolId: _config.cognito.userPoolId,
        ClientId: _config.cognito.userPoolClientId
    };

    var userPool;

    userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

    if (typeof AWSCognito !== 'undefined') {
        AWSCognito.config.region = _config.cognito.region;
    }

    Snerted.signOut = function signOut() {
        userPool.getCurrentUser().signOut();
        window.location.href = signinUrl;
    };

    Snerted.authToken = new Promise(function fetchCurrentAuthToken(resolve, reject) {
        var cognitoUser = userPool.getCurrentUser();

        if (cognitoUser) {
            cognitoUser.getSession(function sessionCallback(err, session) {
                if (err) {
                    reject(err);
                } else if (!session.isValid()) {
                    resolve(null);
                } else {
                    resolve(session.getIdToken().getJwtToken());
                }
            });
        } else {
            resolve(null);
        }
    });


    /*
     * Cognito User Pool functions
     */

    function register(email, password, onSuccess, onFailure) {
        var dataEmail = {
            Name: 'email',
            Value: email
        };
        var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);

        userPool.signUp(toUsername(email), password, [attributeEmail], null,
            function signUpCallback(err, result) {
                if (!err) {
                    onSuccess(result);
                } else {
                    onFailure(err);
                }
            }
        );
    }

    function signin(email, password, onSuccess, onFailure) {
        var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails({
            Username: toUsername(email),
            Password: password
        });

        var cognitoUser = createCognitoUser(email);
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: onSuccess,
            onFailure: onFailure
        });
    }

    function verify(email, code, onSuccess, onFailure) {
        createCognitoUser(email).confirmRegistration(code, true, function confirmCallback(err, result) {
            if (!err) {
                onSuccess(result);
            } else {
                onFailure(err);
            }
        });
    }

    function createCognitoUser(email) {
        return new AmazonCognitoIdentity.CognitoUser({
            Username: toUsername(email),
            Pool: userPool
        });
    }

    function toUsername(email) {
        return email.replace('@', '-at-');
    }

    /*
     *  Event Handlers
     */

    $(function onDocReady() {
        $('#signinForm').submit(handleSignin);
        $('#registrationForm').submit(handleRegister);
        $('#verifyForm').submit(handleVerify);
    });

    function handleSignin(event) {
        var email = $('#emailInputSignin').val();
        var password = $('#passwordInputSignin').val();
        event.preventDefault();
        signin(email, password,
            function signinSuccess() {
                console.log('Successfully Logged In');
                window.location.href = 'index.html';
            },
            function signinError(err) {
                info.innerHTML = alert_msg('danger', err);
            }
        );
    }

    function handleRegister(event) {
        var email = $('#emailInputRegister').val();
        var password = $('#passwordInputRegister').val();
        var password2 = $('#password2InputRegister').val();

        var onSuccess = function registerSuccess(result) {
            var cognitoUser = result.user;
            console.log('user name is ' + cognitoUser.getUsername());
            window.location.href = 'verify.html';
        };
        var onFailure = function registerFailure(err) {
            info.innerHTML = alert_msg('danger', err);
        };
        event.preventDefault();

        if (password === password2) {
            register(email, password, onSuccess, onFailure);
        } else {
            info.innerHTML = alert_msg('danger', 'Passwords do not match');
        }
    }

    function handleVerify(event) {
        var email = $('#emailInputVerify').val();
        var code = $('#codeInputVerify').val();
        event.preventDefault();
        verify(email, code,
            function verifySuccess(result) {
                console.log('call result: ' + result);
                console.log('Successfully verified');
                window.location.href = signinUrl;
            },
            function verifyError(err) {
                info.innerHTML = alert_msg('danger', err);
            }
        );
    }
}(jQuery));