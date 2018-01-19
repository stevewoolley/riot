var Snerted = window.Snerted || {};

function publish(key, title) {
    $.ajax({
        url: _config.api.invokeUrl + '/actions/' + key,
        crossOrigin: true,
        headers: {
            Authorization: Snerted.token
        },
        success: function (data) {
            info.innerHTML = alert_msg('success', title);
        },
        error: function (err) {
            info.innerHTML = alert_msg('danger', err.code);
        }
    });

}


(function authScopeWrapper($) {
    Snerted.authToken.then(function setAuthToken(token) {
        if (token) {
            Snerted.token = token;
        } else {
            window.location.href = 'login.html';
        }
    }).catch(function handleTokenError(error) {
        info.innerHTML = alert_msg('danger', error);
        window.location.href = 'login.html';
    });

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
        $('#logout-nav').show().append('<a class="nav-link" title="Logout" onclick="Snerted.signOut()">Logout</a>');
    }

    function unauthMenuSet() {
        emptyMenuSet();
        $('#logout-nav').hide();
        $('#settings-nav').hide();
        $('#actions-nav').hide();
        $('#snapshots-nav').hide();
        $('#things-nav').hide();
        $('#login-nav').show().append('<a class="nav-link" title="Login" href="login.html">Login</a>');
    }

    $(function onDocReady() {
        Snerted.authToken.then(function updateAuthMessage(token) {
            if (token) {
                // authenticated
                authMenuSet();
            } else {
                // unauthenticated
                unauthMenuSet();
            }
        });
    });

}(jQuery));