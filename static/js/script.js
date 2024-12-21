document.getElementById('modelo-select').addEventListener('change', function() {
    const selectedModel = this.value;
    axios.post('/cambiar_modelo', { modelo: selectedModel })
        .then(response => {
            if (response.data.success) {
                alert(response.data.mensaje);
            }
        })
        .catch(error => {
            console.error('Error al cambiar modelo:', error);
        });
});

function addMessage(messageText, isUser, container) {
    const messageDiv = document.createElement('div');
    messageDiv.innerHTML = marked.parse(messageText);
    messageDiv.classList.add('message', isUser ? 'user-message' : 'bot-message');

    // Crear botón de copiar
    const copyButton = document.createElement('button');
    copyButton.textContent = 'Copiar';
    copyButton.classList.add('copy-button');
    copyButton.onclick = function() {
        try {
            // Crear un elemento temporal de texto
            const tempTextArea = document.createElement('textarea');
            tempTextArea.value = messageText;
            document.body.appendChild(tempTextArea);
            
            // Seleccionar el texto
            tempTextArea.select();
            tempTextArea.setSelectionRange(0, 99999); // Para dispositivos móviles

            // Intentar copiar
            const successful = document.execCommand('copy');
            
            // Eliminar elemento temporal
            document.body.removeChild(tempTextArea);

            if (successful) {
                copyButton.textContent = '¡Copiado!';
                copyButton.classList.add('copied');
                setTimeout(() => {
                    copyButton.textContent = 'Copiar';
                    copyButton.classList.remove('copied');
                }, 1500);
            } else {
                throw new Error('Copia fallida');
            }
        } catch (err) {
            console.error('Error al copiar:', err);
            try {
                // Método de Clipboard API como respaldo
                navigator.clipboard.writeText(messageText).then(() => {
                    copyButton.textContent = '¡Copiado!';
                    copyButton.classList.add('copied');
                    setTimeout(() => {
                        copyButton.textContent = 'Copiar';
                        copyButton.classList.remove('copied');
                    }, 1500);
                }).catch(() => {
                    copyButton.textContent = 'Error al copiar';
                    setTimeout(() => {
                        copyButton.textContent = 'Copiar';
                    }, 1500);
                });
            } catch (clipboardErr) {
                alert('No se pudo copiar el texto. Por favor, cópielo manualmente.');
            }
        }
    };

    messageDiv.appendChild(copyButton);
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');
    const typingIndicator = document.querySelector('.typing-indicator');
    const message = userInput.value.trim();

    if (message === '') return;

    // Mensaje del usuario
    addMessage(message, true, chatContainer);

    // Limpiar input
    userInput.value = '';

    // Mostrar indicador de escribiendo
    typingIndicator.style.display = 'block';

    // Enviar mensaje al backend
    axios.post('/chat', { message: message })
        .then(response => {
            // Ocultar indicador de escribiendo
            typingIndicator.style.display = 'none';

            if (response.data.success) {
                addMessage(response.data.response, false, chatContainer)
            } else {
                console.error('Error en la respuesta del chatbot');
            }
        })
        .catch(error => {
            // Ocultar indicador de escribiendo
            typingIndicator.style.display = 'none';
            console.error('Error al enviar mensaje:', error);
        });
}

// Permitir envío con tecla Enter
document.getElementById('user-input').addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});