$(document).ready(function(){
    var ShowForm = function(){
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function(){
                $('#modal-paydash').modal('show');
            },
            success: function(data){
                $('#modal-paydash .modal-content').html(data.html_form);
            }
        });
    };
    var SaveForm = function() {
        var form = $(this);
        $.ajax({
            url: form.attr('data-url'),
            data: form.serialize(),
            type: form.attr('method'),
            dataType: 'json',
            success: function(data) {
                if(data.form_is_valid) {
                    $('#example3 tbody').html(data.paydash);
                    $('#modal-paydash').modal('hide');
                } else {
                    $('#modal-paydash .modal-content').html(data.html_form)
                }
            }
        })
        return false;
    };

// Update form
$('#example3').on("click", ".show-form-update", ShowForm);
$('#modal-paydash').on("submit", ".update-form", SaveForm);

});