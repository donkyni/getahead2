$(document).ready(function(){
    var ShowForm = function(){
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function(){
                $('#modal-groupe').modal('show');
            },
            success: function(data){
                $('#modal-groupe .modal-content').html(data.html_form);
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
                    $('#example3 tbody').html(data.groupe);
                    $('#modal-groupe').modal('hide');
                } else {
                    $('#modal-groupe .modal-content').html(data.html_form)
                }
            }
        })
        return false;
    };

// Create a form
$(".show-form").click(ShowForm);
$('#modal-groupe').on("submit", ".create-form", SaveForm);

// Update form
$('#example3').on("click", ".show-form-update", ShowForm);
$('#modal-groupe').on("submit", ".update-form", SaveForm);

// Delete form
$('#example3').on("click", ".show-form-delete", ShowForm);
$('#modal-groupe').on("submit", ".delete-form", SaveForm);

});