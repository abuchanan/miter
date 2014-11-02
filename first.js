function UserProfileCtrl(inject) {
  var userId = inject('Request').params.userId;
  var user = inject('Users').get(userId);
  var session = inject('Sessions').get(Inject('Request').cookies.sessionId);
  if (session.user.id === user.id) {
    var formData = inject('Request').formData;
    // TODO but how do you do function calls in things are injected?
    if (inject('UserProfileFormValidates')(formData)) {
      // ... etc ...
    }
  }
}

UserProfileCtrl.bind('UserProfileFormValidates', 

function UserProfileFormValidates(data) {
  return false;
}
