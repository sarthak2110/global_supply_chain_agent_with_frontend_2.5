// public/blob.js

document.addEventListener("DOMContentLoaded", () => {
    // 1. Create Orbs
    ["up", "down", "left", "right"].forEach(id => {
        if (!document.getElementById(id)) {
            const orb = document.createElement("div");
            orb.id = id;
            document.body.appendChild(orb);
        }
    });

    // 2. Custom Toggle UI
    const toggleContainer = document.createElement('div');
    toggleContainer.id = 'gemini-mode-toggle';
    toggleContainer.innerHTML = `
        <div class="mode-btn active" data-mode="fast">⚡ Fast</div>
        <div class="mode-btn" data-mode="thinking">🧠 Thinking</div>
        <div class="mode-btn" data-mode="pro">💎 Pro</div>
    `;

    const style = document.createElement('style');
    style.innerHTML = `
        #gemini-mode-toggle { display: flex; background: var(--custom-input-bg); border: 1px solid var(--primary-blue); border-radius: 20px; overflow: hidden; margin-right: 12px; height: 36px; z-index: 50; backdrop-filter: blur(10px); }
        .mode-btn { padding: 0 14px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.85rem; font-weight: 600; color: var(--custom-input-text); transition: all 0.2s; border-right: 1px solid rgba(37, 99, 235, 0.2); }
        .mode-btn.active { background: var(--primary-blue); color: #ffffff; }
        .mode-btn:hover:not(.active) { background: rgba(37, 99, 235, 0.1); }
    `;
    document.head.appendChild(style);

    let currentMode = "fast";
    toggleContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('.mode-btn');
        if (btn) {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
        }
    });

    // 3. UI Fixer: Move toggle and clean up "Used" labels
    const observer = new MutationObserver(() => {
        const submitBtn = document.getElementById('chat-submit');
        if (submitBtn && !submitBtn.parentElement.contains(toggleContainer)) {
            submitBtn.parentElement.insertBefore(toggleContainer, submitBtn);
        }

        // Clean up steps to look like Gemini
        document.querySelectorAll('div[data-step-type="run"]').forEach(step => {
            const header = step.querySelector('p.text-muted-foreground');
            if (header) {
                header.childNodes.forEach(node => {
                    if (node.nodeType === 3 && node.textContent.includes('Used')) node.textContent = '';
                });
                const icon = step.querySelector('.ai-message > span.inline-block');
                if (icon) icon.style.display = 'none';
            }
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // 4. Invisible Tagging
    const interceptSend = () => {
        const textarea = document.getElementById('chat-input');
        if (textarea && textarea.value.trim() !== "") {
            const tags = {"fast": "\u200B", "thinking": "\u200C", "pro": "\u200D"};
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            setter.call(textarea, textarea.value + tags[currentMode]);
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };

    document.body.addEventListener('mousedown', (e) => { if (e.target.closest('#chat-submit')) interceptSend(); }, true);
    document.body.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) interceptSend(); }, true);
});