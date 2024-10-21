$(document).ready(function(){
    var ShowForm = function(){
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function(){
                $('#modal-panier').modal('show');
            },
            success: function(data){
                $('#modal-panier .modal-content').html(data.html_form);
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
                    $('#example3 tbody').html(data.panier);
                    $('#modal-panier').modal('hide');
                } else {
                    $('#modal-panier .modal-content').html(data.html_form)
                }
            }
        })
        return false;
    };


// Update form
$('#example3').on("click", ".show-form-update", ShowForm);
$('#modal-panier').on("submit", ".update-form", SaveForm);

// Delete form
$('#example3').on("click", ".show-form-delete", ShowForm);
$('#modal-panier').on("submit", ".delete-form", SaveForm);

});