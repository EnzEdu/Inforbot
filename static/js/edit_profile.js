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

// Editar dados
function habilitarEdicao(id) {
    const campo = document.getElementById(id);
    if (campo) {
        campo.removeAttribute('readonly');
        campo.classList.add('editavel');
        campo.focus();
    }
}

// Cancelar edição
function cancelarEdicao() {
    if (confirm('Deseja cancelar as alterações?')) {
        window.location.href = "dashboard.html";
    }
}