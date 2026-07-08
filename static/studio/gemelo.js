// Stonelytics Studio — Twin Visualization

function toggleCapa(id) {
    const content = document.getElementById('capa-content-' + id);
    const icon = document.getElementById('capa-icon-' + id);
    if (content.style.display === 'none' || !content.style.display) {
        content.style.display = 'block';
        icon.classList.replace('ti-chevron-right', 'ti-chevron-down');
    } else {
        content.style.display = 'none';
        icon.classList.replace('ti-chevron-down', 'ti-chevron-right');
    }
}

function editarCapa(capaId) {
    const modal = document.getElementById('modal-capa');
    const textarea = document.getElementById('capa-editor');
    const currentContent = document.getElementById('capa-json-' + capaId);
    
    document.getElementById('modal-capa-title').textContent = 'Editando: ' + capaId;
    document.getElementById('modal-capa-id').value = capaId;
    
    if (currentContent) {
        const content = JSON.parse(currentContent.value);
        textarea.value = JSON.stringify(content, null, 2);
    }
    
    modal.style.display = 'flex';
}

function cerrarModal() {
    document.getElementById('modal-capa').style.display = 'none';
}

async function guardarCapa() {
    const capaId = document.getElementById('modal-capa-id').value;
    const content = document.getElementById('capa-editor').value;
    
    try {
        JSON.parse(content);
    } catch (e) {
        alert('JSON inválido. Corrige antes de guardar.');
        return;
    }
    
    const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/gemelo-asis`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ capas: { [capaId]: JSON.parse(content) } }),
    });
    const data = await resp.json();
    if (data.ok) {
        cerrarModal();
        location.reload();
    } else {
        alert('Error: ' + data.error);
    }
}

async function calcularBrechas() {
    const btn = document.getElementById('btn-calcular-brechas');
    btn.disabled = true;
    btn.textContent = 'Calculando...';
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/calcular-brechas`, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            window.location.href = `/studio/${CONSULTORIA_ID}/brechas`;
        } else {
            alert('Error: ' + data.error);
        }
    } catch (e) {
        alert('Error de conexión');
    }
    
    btn.disabled = false;
    btn.textContent = 'Calcular Brechas';
}

async function generarPlan() {
    const btn = document.getElementById('btn-generar-plan');
    btn.disabled = true;
    btn.textContent = 'Generando...';
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/generar-plan`, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            window.location.href = `/studio/${CONSULTORIA_ID}/plan`;
        } else {
            alert('Error: ' + data.error);
        }
    } catch (e) {
        alert('Error de conexión');
    }
    
    btn.disabled = false;
    btn.textContent = 'Generar Plan';
}

async function sugerirTobe(capa) {
    const btn = document.getElementById('sugerir-' + capa);
    if (btn) btn.disabled = true;
    
    const contenidoEl = document.getElementById('capa-json-' + capa);
    const contenido = contenidoEl ? JSON.parse(contenidoEl.value) : {};
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/sugerir-tobe`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ capa, contenido }),
        });
        const data = await resp.json();
        if (data.ok && data.objetivos) {
            const container = document.getElementById('objetivos-' + capa);
            if (container) {
                container.innerHTML = data.objetivos.map((o, i) =>
                    `<div class="objetivo-item"><input type="checkbox" checked> <span>${o.descripcion}</span> <span class="badge badge--${o.prioridad === 'alta' ? 'error' : 'warning'}">${o.prioridad}</span></div>`
                ).join('');
            }
        }
    } catch (e) {
        console.error('Error suggesting TO BE:', e);
    }
    
    if (btn) btn.disabled = false;
}

document.addEventListener('click', function(e) {
    const modal = document.getElementById('modal-capa');
    if (modal && e.target === modal) cerrarModal();
});
