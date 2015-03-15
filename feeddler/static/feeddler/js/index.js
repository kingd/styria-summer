$(function() {
    $('.feed').click(function(event){
        var csrftoken = get_cookie('csrftoken');
        var url = $(this).data('url');
        var feed_id = $(this).data('feed_id');
        var data = {
            'feed_id': feed_id,
            'csrfmiddlewaretoken': csrftoken,
        }
        var that = this;
        $.post(
            url,
            data,
            function (result) {
                if (result['success']) {
                    console.log(result);
                    if (result['is_active']) {
                        $(that).addClass('btn-success');
                        $(that).removeClass('btn-default');
                    } else {
                        $(that).addClass('btn-default');
                        $(that).removeClass('btn-success');
                    }
                    $(that).text(result['result']);
                } else {
                    alert('Update failed');
                }
            },
            'json'
        );
    });
});

function get_cookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
