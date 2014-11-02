function UserProfileCtrl(inject) {

  var userId = Request.params.userId;
  var user = Users.get(userId);

  // OR

  var userId  = RequestParams.userId;

  // OR

  var sessionId = Request.cookies.sessionId;
  var session = Sessions.get(sessionId);
  var currentUser = session.user;

  // OR

  var currentUser = Request.currentUser;


  if (currentUser.id === user.id) {
    var formData = Request.formData;
    // TODO but how do you do function calls in things are injected?
    if (UserProfileFormValidates(formData)) {
      // ... etc ...
    }
  }
}

UserProfileCtrl.bind('UserProfileFormValidates', 

function UserProfileFormValidates(data) {
  return false;
}
