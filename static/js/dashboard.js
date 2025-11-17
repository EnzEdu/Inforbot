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

// --- 1. GESTÃO DO ID DE SESSÃO ÚNICO ---
const SESSION_KEY = 'chat-user-id';

function getOrCreateSessionId() {
    let sessionId = localStorage.getItem(SESSION_KEY);
    
    // Se não houver ID, gera um novo (UUID simples)
    if (!sessionId) {
        sessionId = crypto.randomUUID(); // Usa a API Web Crypto para gerar um UUID
        localStorage.setItem(SESSION_KEY, sessionId);
        console.log("Novo ID de Sessão gerado:", sessionId);
    } else {
        console.log("ID de Sessão existente:", sessionId);
    }
    return sessionId;
}

// Inicializa o ID de sessão quando o script é carregado
const userId = getOrCreateSessionId();


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
                // O ID de sessão é o ponto-chave para o backend manter o histórico isolado
                session_id: userId, 
                message: userMessage,
                conversa_id: conversaAtualId,
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