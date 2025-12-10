/*Função realiza a troca entre o ícone e a foto selecionada */
function mostrarPreview(event) {
    const input = event.target;
    const preview = document.getElementById('preview-img');
    const icon = document.getElementById('icon-default');

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            // Define a fonte da imagem como o arquivo carregado
            preview.src = e.target.result;
            
            // Esconde o ícone e mostra a imagem
            preview.style.display = 'block';
            icon.style.display = 'none';
        }

        reader.readAsDataURL(input.files[0]);
    } else {
        // Se o usuário cancelar, volta ao normal
        preview.style.display = 'none';
        icon.style.display = 'block';
        preview.src = '#';
    }
}

// Validar no formulário a senha
function validarFormulario(event) {
    const senha = document.getElementById('senha').value;
    const confirmar_senha = document.getElementById('confirmar_senha').value;
    if (senha !== confirmar_senha) {
        alert('As senhas não coincidem!');
        event.preventDefault();
        return false;
    }
    if (senha.length < 6) {
        alert('A senha deve ter pelo menos 6 caracteres!');
        event.preventDefault();
        return false;
    }
    return true;
}

document.getElementById("my-form").addEventListener("submit", function(event) {
    event.preventDefault(); // stop normal form submit

    const form = event.target;
    const formData = new FormData(form); // includes all fields inside the form

    // include the file from outside the form
    const fileInput = document.getElementById("foto_upload");
    if (fileInput.files.length > 0) {
        formData.append("foto_perfil", fileInput.files[0]);
    }

    // send using fetch WITHOUT await
    fetch(form.action, {
        method: "POST",
        body: formData
    }).then(() => {
        window.location.href = "/login";
    });

    // optional: show loading / disable button / etc.
});


// Apresenta erros durante o registro
function apresentarErro(msg) {
    alert(msg);
    return false;
}