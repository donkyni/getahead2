$(document).ready(function(){
    var ShowForm = function(){
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function(){
                $('#modal-prixproduit').modal('show');
            },
            success: function(data){
                $('#modal-prixproduit .modal-content').html(data.html_form);
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
                    $('#example3 tbody').html(data.prixproduit);
                    $('#modal-prixproduit').modal('hide');
                } else {
                    $('#modal-prixproduit .modal-content').html(data.html_form)
                }
            }
        })
        return false;
    };

// Create a form
$(".show-form").click(ShowForm);
$('#modal-prixproduit').on("submit", ".create-form", SaveForm);

// Update form
$('#example3').on("click", ".show-form-update", ShowForm);
$('#modal-prixproduit').on("submit", ".update-form", SaveForm);

// Delete form
$('#example3').on("click", ".show-form-delete", ShowForm);
$('#modal-prixproduit').on("submit", ".delete-form", SaveForm);

});