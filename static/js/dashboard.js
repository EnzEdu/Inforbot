// Adicionando o comportamento para o botão "Sair"
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function(event) {
            event.preventDefault();
            // Redireciona para a pág de login e substitui a pág atual no histórico
            window.location.href = "/logout";
        });
    }
});

// Exemplo de código JS para redimensionamento automático do textarea
const textarea = document.getElementById('user-input');
textarea.addEventListener('input', () => {
    // Redefine a altura para 'auto' para recalcular o scrollHeight
    textarea.style.height = 'auto'; 
    // Define a nova altura com base no conteúdo, respeitando o max-height do CSS
    textarea.style.height = textarea.scrollHeight + 'px';
});

// --- 2. LÓGICA DE ENVIO E RECEBIMENTO DE MENSAGENS ---
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatWindow = document.getElementById('chat-window');

// Função para adicionar uma mensagem à janela de chat
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    chatWindow.appendChild(messageDiv);
    
    // Rola para o final da janela de chat para mostrar a nova mensagem
    chatWindow.scrollTop = chatWindow.scrollHeight; 
}

// Evento de envio do formulário
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Impede o recarregamento da página
    
    const userMessage = userInput.value.trim();
    if (userMessage === '') return; // Não envia mensagens vazias

    const checkedValues = Array.from(
        document.querySelectorAll(".pdf-checkbox:checked")
    ).map(cb => cb.value);
    console.log("Itens:", checkedValues);


    // 1. Exibe a mensagem do usuário
    addMessage('user', userMessage);
    userInput.value = ''; // Limpa o campo de entrada

    try {
        // 2. Faz a requisição para o Backend (Flask/LangChain)
        const response = await fetch('/api/chat', { // Você deve criar esta rota no Flask
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: "teste", 
                message: userMessage,
                conversa_id: conversaAtualId,
                documentosEscolhidos: checkedValues,
            }),
        });

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const data = await response.json();
        const botResponse = data.response || "Desculpe, não consegui obter uma resposta.";

        // 3. Exibe a resposta do bot
        addMessage('bot', botResponse);

    } catch (error) {
        console.error('Erro ao comunicar com o backend:', error);
        addMessage('bot', 'Ocorreu um erro na comunicação com o servidor.');
    }
});

// Constante de 50MB (definida globalmente)
const LIMITE_CONTA_BYTES = 50 * 1024 * 1024; // 50MB

function validarUpload(input) {
    if (input.files && input.files[0]) {
        const arquivo = input.files[0];
        const tamanhoNovoArquivo = arquivo.size;

        // "usoTotalBytes" é a variável que criamos no script do HTML
        // Se ela não estiver definida por algum erro, assumimos 0
        //const ocupadoAtualmente = (typeof usoTotalBytes !== 'undefined') ? usoTotalBytes : 0;

        //const previsaoTotal = ocupadoAtualmente + tamanhoNovoArquivo;

        // 1. Validação: A soma ultrapassa o limite?
        if (tamanhoNovoArquivo > LIMITE_CONTA_BYTES) {
            // Cálculos para mostrar mensagem bonita em MB
            const livre = 1984; //(LIMITE_CONTA_BYTES - ocupadoAtualmente) / (1024 * 1024);
            const tamanhoArquivoMB = tamanhoNovoArquivo / (1024 * 1024);

            alert(`Upload negado!\n\nTamanho máximo suportado para PDFs: 50 MB\nSeu arquivo: ${tamanhoArquivoMB.toFixed(2)} MB`);
            
            input.value = ""; // Limpa o input
            return;
        }

        // Se passou, envia!
        document.getElementById('upload-form').submit();
    }
}

// Deletar pdf
async function deletarPdf(pdfId) {
    if (!confirm("Tem certeza que deseja excluir este PDF?")) return;

    try {
        const response = await fetch(`/deletar_pdf/${pdfId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 1. Remove o item visual da lista
            const itemParaRemover = document.querySelector(`.pdf-item[data-id="${pdfId}"]`);
            if (itemParaRemover) itemParaRemover.remove();

            // 2. ATUALIZA A BARRA DE PROGRESSO E O TEXTO
            // O backend nos mandou o 'novo_uso_bytes'
            //atualizarBarraArmazenamento(data.novo_uso_bytes);

            // Atualiza a variável global para validações futuras de upload
            //usoTotalBytes = data.novo_uso_bytes; 
            
        } else {
            alert("Erro ao excluir: " + (data.error || "Erro desconhecido"));
        }
    } catch (error) {
        console.error("Erro:", error);
        alert("Erro de conexão.");
    }
}

// Auxiliar para atualizar a UI da barra
function atualizarBarraArmazenamento(bytesAtuais) {
    const LIMITE = 50 * 1024 * 1024; // 50MB
    
    // Converte para MB
    const mbUsados = (bytesAtuais / (1024 * 1024)).toFixed(2);
    
    // Calcula porcentagem (limitada a 100%)
    let porcentagem = (bytesAtuais / LIMITE) * 100;
    if (porcentagem > 100) porcentagem = 100;
    if (porcentagem < 0) porcentagem = 0;

    // Atualiza o Texto no HTML
    // Seleciona o span que contem o texto "XX.XXMB / 50MB"
    const textoContainer = document.querySelector('.storage-text span:last-child');
    if (textoContainer) {
        textoContainer.innerText = `${mbUsados}MB / 50MB`;
    }

    // Atualiza a Largura da Barra
    const barraFill = document.querySelector('.progress-bar-fill');
    if (barraFill) {
        barraFill.style.width = `${porcentagem}%`;
        
        // Opcional: Mudar cor se estiver cheio
        if (porcentagem > 90) {
            barraFill.style.backgroundColor = 'red';
        } else {
            barraFill.style.backgroundColor = '#5bb1b0';
        }
    }
}