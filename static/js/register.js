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