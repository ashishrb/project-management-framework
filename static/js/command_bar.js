// Minimal AI Command Bar for quick natural queries
(function(){
    let mounted = false;
    let csrfToken = null;

    async function getCSRFToken() {
        if (csrfToken) return csrfToken;
        try {
            const res = await fetch('/csrf-token');
            const data = await res.json();
            csrfToken = data.csrf_token;
            return csrfToken;
        } catch {
            return '';
        }
    }

    function mount() {
        if (mounted) return;
        mounted = true;
        const bar = document.createElement('div');
        bar.id = 'ai-command-bar';
        bar.style.position = 'fixed';
        bar.style.top = '50%';
        bar.style.right = '0';
        bar.style.transform = 'translateY(-50%)';
        bar.style.width = '360px';
        bar.style.maxWidth = '90vw';
        bar.style.background = '#ffffff';
        bar.style.border = '1px solid #dee2e6';
        bar.style.borderRight = '0';
        bar.style.borderRadius = '8px 0 0 8px';
        bar.style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)';
        bar.style.zIndex = '1050';
        bar.style.display = 'none';

        bar.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border-bottom:1px solid #eee;">
                <strong><i class="fas fa-robot me-1"></i> AI Command Bar</strong>
                <button id="ai-cb-close" class="btn btn-sm btn-outline-secondary">Close</button>
            </div>
            <div style="padding:12px;">
                <div class="input-group mb-2">
                    <input id="ai-cb-input" type="text" class="form-control" placeholder="Ask or type a command (e.g., show at-risk projects)">
                    <button id="ai-cb-send" class="btn btn-primary"><i class="fas fa-paper-plane"></i></button>
                </div>
                <small id="ai-cb-hint" class="text-muted">Examples: "navigate to portfolio dashboard", "explain ROI trend", "list risks for Project X"</small>
                <div id="ai-cb-output" class="mt-2" style="max-height:240px;overflow:auto;font-size:0.9rem;color:#444;"></div>
            </div>
        `;

        document.body.appendChild(bar);

        document.getElementById('ai-cb-close').onclick = () => toggle(false);
        document.getElementById('ai-cb-send').onclick = () => submit();
        document.getElementById('ai-cb-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') submit();
        });

        // Add floating toggle button
        const fab = document.createElement('button');
        fab.id = 'ai-cb-toggle';
        fab.className = 'btn btn-primary';
        fab.style.position = 'fixed';
        fab.style.right = '16px';
        fab.style.bottom = '16px';
        fab.style.borderRadius = '50%';
        fab.style.width = '48px';
        fab.style.height = '48px';
        fab.style.zIndex = '1050';
        fab.innerHTML = '<i class="fas fa-robot"></i>';
        fab.onclick = () => toggle();
        document.body.appendChild(fab);
    }

    function toggle(force) {
        const bar = document.getElementById('ai-command-bar');
        if (!bar) return;
        const show = typeof force === 'boolean' ? force : bar.style.display === 'none';
        bar.style.display = show ? 'block' : 'none';
        if (show) {
            setTimeout(() => {
                const input = document.getElementById('ai-cb-input');
                if (input) input.focus();
            }, 50);
        }
    }

    async function submit() {
        const input = document.getElementById('ai-cb-input');
        const out = document.getElementById('ai-cb-output');
        if (!input || !out) return;
        const text = input.value.trim();
        if (!text) return;
        const snapshot = text;
        input.value = '';
        out.innerHTML = `<div><span class="text-primary">You:</span> ${escapeHtml(snapshot)}</div>` + out.innerHTML;
        try {
            const token = await getCSRFToken();
            const res = await fetch('/api/v1/ai/copilot/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': token || ''
                },
                body: JSON.stringify({ message: snapshot, mode: 'fast', csrf_token: token || '' })
            });
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const data = await res.json();
            const ai = data.response || 'No response';
            out.innerHTML = `<div class="mt-2"><span class="text-success">AI:</span> ${format(ai)}</div>` + out.innerHTML;
            // Simple smart navigation hooks
            routeIfNavigation(snapshot);
        } catch (e) {
            out.innerHTML = `<div class="mt-2 text-danger">Error: ${escapeHtml(String(e))}</div>` + out.innerHTML;
        }
    }

    function routeIfNavigation(text) {
        const t = text.toLowerCase();
        if (t.includes('portfolio dashboard')) {
            window.location.href = '/dashboard/portfolio';
        } else if (t.includes('manager dashboard') || t.includes('owner dashboard')) {
            window.location.href = '/dashboard/manager';
        } else if (t.includes('admin')) {
            window.location.href = '/admin';
        } else if (t.startsWith('go to ') || t.startsWith('navigate to ')) {
            const path = t.replace(/^go to |^navigate to /, '').trim();
            if (path.startsWith('/')) window.location.href = path;
        }
    }

    function format(text) {
        return escapeHtml(text).replace(/\n/g, '<br>');
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"]+/g, (c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    }

    document.addEventListener('DOMContentLoaded', mount);
    window.AICommandBar = { toggle };
})();
