var btnUpload = $("#upload_file"),
	btnOuter = $(".button_outer");
btnUpload.on("change", function (e) {
	var ext = btnUpload.val().split('.').pop().toLowerCase();
	if ($.inArray(ext, ['gif', 'png', 'jpg', 'jpeg']) == -1) {
		$(".error_msg").text("Not an Image...");
	} else {
		$(".error_msg").text("");
		btnOuter.addClass("file_uploading");
		setTimeout(function () {
			btnOuter.addClass("file_uploaded");
		}, 3000);
		var uploadedFile = URL.createObjectURL(e.target.files[0]);
		setTimeout(function () {
			$("#uploaded_view").append('<img src="' + uploadedFile + '" />').addClass("show");
		}, 3500);
	}
});
$(".file_remove").on("click", function (e) {
	$("#uploaded_view").removeClass("show");
	$("#uploaded_view").find("img").remove();
	btnOuter.removeClass("file_uploading");
	btnOuter.removeClass("file_uploaded");
});

$(document).ready(function (e) {
	function getMessage(variation) {
		// menor que 30
		if (variation <= 30)
			msg = "Baixa probabilidade de possuir sintomas do retinoblastoma"
		// entre 30 e 60
		if (variation > 30 && variation <= 60)
			msg = "Existe a possibilidade de possuir os sintomas do retinoblastoma, recomendamos um diagnóstico mais preciso com um médico"
		// maior que 60
		if (variation > 60)
			msg = "Alta probabilidade de possuir os sintomas do retinoblastoma, recomendamos realizar uma consulta com um médico"

		return msg;
	  }

    $('#imageUploadForm').on('submit',(function(e) {
        e.preventDefault();
        var formData = new FormData(this);
		alertify.set('notifier','position', 'top-right');

        $.ajax({
            type:'POST',
            url: $(this).attr('action'),
            data:formData,
            cache:false,
            contentType: false,
            processData: false,
            success:function(data){
				if (Object.hasOwn(data, 'percent_variation')) {
					msg = getMessage(data.percent_variation)
					alertify.alert('Resultado', msg)
				} else {
					alertify.error('Erro ao processar imagem');
					console.log(data);
				}
            },
            error: function(data){
                alertify.error('Erro ao processar imagem, lembre-se de enviar a foto do rosto, com os olhos abertos em um local bem iluminado');
                console.log(data);
            },
        });
    }));
});