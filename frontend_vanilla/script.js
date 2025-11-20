document.getElementById('generateForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('title').value;
    const body = document.getElementById('body').value;
    const platformCheckboxes = document.querySelectorAll('input[name="platform"]:checked');
    const platforms = Array.from(platformCheckboxes).map(cb => cb.value);

    const btn = document.getElementById('generateBtn');
    const btnText = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.loader');
    const resultsSection = document.getElementById('resultsSection');

    if (platforms.length === 0) {
        alert('Por favor selecciona al menos una plataforma.');
        return;
    }

    // UI Loading State
    btn.disabled = true;
    btnText.textContent = 'Generando...';
    loader.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    resultsSection.innerHTML = '';

    try {
        const response = await fetch('http://127.0.0.1:8080/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                body,
                platforms
            })
        });

        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);

    } catch (error) {
        console.error(error);
        resultsSection.innerHTML = `<div class="error-msg">Ocurrió un error: ${error.message}</div>`;
        resultsSection.classList.remove('hidden');
    } finally {
        // Reset UI
        btn.disabled = false;
        btnText.textContent = 'Generar Contenido';
        loader.classList.add('hidden');
    }
});

function renderResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.remove('hidden');

    for (const [platform, content] of Object.entries(data)) {
        const card = document.createElement('div');
        card.className = 'result-card';

        // Handle Errors inside platform response
        if (content.error) {
            card.innerHTML = `
                <div class="card-header" style="background: rgba(239, 68, 68, 0.2);">
                    <span>${platform}</span>
                </div>
                <div class="card-body">
                    <p class="error-msg">${content.message}</p>
                </div>
            `;
            resultsSection.appendChild(card);
            continue;
        }

        let mediaHtml = '';
        if (content.video_url) {
            // Use display_video_url if available, otherwise fallback to video_url
            const videoSrc = content.display_video_url || content.video_url;
            mediaHtml = `
                <div class="media-preview">
                    <video controls src="${videoSrc}"></video>
                </div>`;
        } else if (content.media_url) {
            // Use display_url (localhost) for viewing, media_url (public) is kept hidden for publishing
            const imageSrc = content.display_url || content.media_url;
            mediaHtml = `
                <div class="media-preview">
                    <img src="${imageSrc}" alt="Generated Image">
                </div>`;
        }

        let textContent = content.text || content.caption || content.message || content.script || '';
        let hashtags = content.hashtags ? content.hashtags.join(' ') : '';

        let publishBtnHtml = '';
        if (['facebook', 'instagram', 'whatsapp', 'linkedin'].includes(platform)) {
            publishBtnHtml = `
                <button class="publish-btn" onclick="publishContent('${platform}', this)">
                    Publicar ahora
                </button>
            `;
        }

        card.innerHTML = `
            <div class="card-header">
                <span>${platform}</span>
            </div>
            <div class="card-body">
                <div class="content-text">${textContent}</div>
                ${hashtags ? `<div class="hashtags">${hashtags}</div>` : ''}
                ${mediaHtml}
                ${publishBtnHtml}
            </div>
            <!-- Hidden data for publishing -->
            <input type="hidden" class="raw-text" value="${textContent.replace(/"/g, '&quot;')}">
            <input type="hidden" class="raw-media" value="${content.media_url || ''}">
        `;
        resultsSection.appendChild(card);
    }
}

async function publishContent(platform, btn) {
    const cardBody = btn.closest('.card-body');
    const card = btn.closest('.result-card');
    const text = card.querySelector('.raw-text').value;
    const mediaUrl = card.querySelector('.raw-media').value;

    if (!confirm(`¿Estás seguro de publicar esto en ${platform}?`)) return;

    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Publicando...';

    try {
        const response = await fetch('http://127.0.0.1:8080/api/publish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform, text, media_url: mediaUrl })
        });

        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.message}`);
        } else {
            alert('¡Publicado exitosamente!');
            btn.textContent = 'Publicado ✅';
            btn.classList.add('success');
        }
    } catch (error) {
        console.error(error);
        alert('Error de conexión al publicar.');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}
