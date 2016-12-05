(function (window) {

  function update (participant_id, tag, callback) {
      var url = '/supervisor/update/' + participant_id;
      var data = { 'data': { 'tag': tag }};
      $.ajax({
          url: url,
          type: 'PUT',
          data: JSON.stringify(data),
          contentType: 'application/json; charset=utf-8',
          dataType: 'json',
          async: true
      })
      .success(function () {
          callback();
      });
  }

  var editor_open = false;

  $('.tag-view').click (function (event_, sender) {
    if(editor_open){
      return;
    }

    editor_open = true;
    var self = $(this);
    self.next().show();
    self.hide();
  });

  $('button.tag-ok').click (function () {
    var self = $(this);
    var input = self.prev().children('input').first();
    var tag = input.val().trim();

    // Empty or nothing changed
    if(!tag || tag == input.data('tag')) {
      return;
    }

    var participant_id = self.data('participant');
    update(participant_id, tag, function closeEditor () {
      editor_open = false;
      var parent = self.parent();
      parent.prev().text(tag).show();
      parent.hide();
    });
  });

  $('button.tag-cancel').click (function () {
    editor_open = false;
    var control = $(this).parent();
    selected_participant_id = null;
    control.prev().show();
    control.hide();
  });

})(window);
