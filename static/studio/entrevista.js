// Stonelytics Studio — Interview Chat (Consulting Reasoning)
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const btnEnviar = document.getElementById('btn-enviar');
const typingIndicator = document.getElementById('typing-indicator');
const capaIndicator = document.getElementById('capa-indicator');
const depthIndicator = document.getElementById('depth-indicator');
const temaIndicator = document.getElementById('tema-indicator');
const btnFinalizar = document.getElementById('btn-finalizar');

let isProcessing = false;

const CAPA_NOMBRES = {
    'proposito': 'Proposito', 'clientes': 'Clientes', 'servicios': 'Servicios',
    'procesos': 'Procesos', 'personas': 'Personas', 'informacion': 'Informacion',
    'tecnologia': 'Tecnologia', 'inteligencia': 'Inteligencia',
    'gobierno': 'Gobierno', 'evolucion': 'Evolucion'
};

const DEPTH_NOMBRES = ['', 'Superficie', 'Prioridad', 'Evidencia', 'Causa Raiz', 'Impacto', 'Necesidad'];

function addMessage(text, isIA) {
    const div = document.createElement('div');
    div.className = 'studio-chat__message studio-chat__message--' + (isIA ? 'ia' : 'user');
    div.innerHTML = `
        <div class="studio-chat__avatar"><i class="ti ti-${isIA ? 'robot' : 'user'}"></i></div>
        <div class="studio-chat__bubble"><p>${text.replace(/\n/g, '<br>')}</p></div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateIndicators(capa, profundidad, tema) {
    if (capa && CAPA_NOMBRES[capa]) {
        capaIndicator.textContent = CAPA_NOMBRES[capa];
    }
    if (profundidad && DEPTH_NOMBRES[profundidad]) {
        depthIndicator.textContent = DEPTH_NOMBRES[profundidad] + ' (' + profundidad + '/6)';
    }
    if (tema) {
        temaIndicator.textContent = tema;
    }
}

function showTyping() {
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    typingIndicator.style.display = 'none';
}

function setProcessing(state) {
    isProcessing = state;
    chatInput.disabled = state;
    btnEnviar.disabled = state;
}

async function enviarMensaje() {
    const mensaje = chatInput.value.trim();
    if (!mensaje || isProcessing) return;
    
    addMessage(mensaje, false);
    chatInput.value = '';
    setProcessing(true);
    showTyping();
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/mensaje`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mensaje }),
        });
        const data = await resp.json();
        hideTyping();
        
        if (data.ok) {
            addMessage(data.mensaje, true);
            updateIndicators(data.capa_actual, data.profundidad, data.tema_actual);
            
            if (data.accion === 'completar') {
                btnFinalizar.style.display = 'inline-flex';
                addMessage('La entrevista esta completa. Haz clic en "Generar Gemelo Digital" para continuar.', true);
            }
        } else {
            addMessage('Error: ' + (data.error || 'Error de conexion'), true);
        }
    } catch (e) {
        hideTyping();
        addMessage('Error de conexion. Verifica tu internet e intenta de nuevo.', true);
    }
    
    setProcessing(false);
}

async function finalizarEntrevista() {
    btnFinalizar.disabled = true;
    btnFinalizar.textContent = 'Generando Blueprint...';
    addMessage('Generando el Blueprint Empresarial completo...', true);
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/generar-blueprint`, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            window.location.href = `/studio/${CONSULTORIA_ID}/gemelo-asis`;
        } else {
            addMessage('Error: ' + (data.error || 'Error generando blueprint'), true);
        }
    } catch (e) {
        addMessage('Error de conexion', true);
    }
    
    btnFinalizar.disabled = false;
    btnFinalizar.textContent = 'Generar Blueprint Empresarial';
}

chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarMensaje();
    }
});

chatInput.focus();
