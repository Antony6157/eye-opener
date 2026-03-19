(() => {
  // ── Element refs ──────────────────────────────────────────
  const overlay     = document.getElementById('settings-overlay');
  const openBtn     = document.getElementById('settings-btn');
  const closeBtn    = document.getElementById('settings-close');
  const saveBtn     = document.getElementById('settings-save');
  const hint        = document.getElementById('settings-hint');
  const portEl      = document.getElementById('flask-port');

  const themeLight  = document.getElementById('theme-light');
  const themeDark   = document.getElementById('theme-dark');

  const providerRadios   = document.querySelectorAll('input[name="llm-provider"]');
  const providerFields   = document.querySelectorAll('.provider-fields');

  const ollamaModelSelect = document.getElementById('ollama-model');
  const ollamaRefreshBtn  = document.getElementById('ollama-refresh');

  if (!overlay || !openBtn) return;

  // ── Theme ─────────────────────────────────────────────────
  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('eo-theme', theme);
    if (themeLight) themeLight.setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
    if (themeDark)  themeDark.setAttribute('aria-pressed',  theme === 'dark'  ? 'true' : 'false');
  }

  // Sync buttons with pre-applied theme (set before paint in <head>)
  applyTheme(document.documentElement.dataset.theme || 'light');

  themeLight?.addEventListener('click', () => applyTheme('light'));
  themeDark?.addEventListener('click',  () => applyTheme('dark'));

  // ── Provider field visibility ─────────────────────────────
  function showProviderFields(provider) {
    providerFields.forEach(el => {
      if (el.dataset.for === provider) {
        el.classList.add('visible');
      } else {
        el.classList.remove('visible');
      }
    });
  }

  providerRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      showProviderFields(radio.value);
      // Auto-fetch Ollama models when switching to Ollama
      if (radio.value === 'ollama') {
        fetchOllamaModels();
      }
    });
  });

  // ── Ollama model fetching ─────────────────────────────────
  async function fetchOllamaModels(currentModel) {
    if (!ollamaModelSelect || !ollamaRefreshBtn) return;

    ollamaRefreshBtn.classList.add('spinning');
    ollamaRefreshBtn.disabled = true;

    try {
      const res = await fetch('/api/ollama-models');
      const data = await res.json();

      // Clear existing options
      ollamaModelSelect.innerHTML = '';

      if (!res.ok || data.status === 'error') {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = `⚠ ${data.error || 'Failed to load models'}`;
        ollamaModelSelect.appendChild(opt);
        return;
      }

      const models = data.models || [];
      if (models.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No models found — pull one with ollama pull';
        ollamaModelSelect.appendChild(opt);
        return;
      }

      models.forEach(name => {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        ollamaModelSelect.appendChild(opt);
      });

      // Select the current model if it's in the list
      if (currentModel && models.includes(currentModel)) {
        ollamaModelSelect.value = currentModel;
      } else if (currentModel) {
        // Current model not in list — add it as a special option
        const opt = document.createElement('option');
        opt.value = currentModel;
        opt.textContent = `${currentModel} (configured)`;
        ollamaModelSelect.insertBefore(opt, ollamaModelSelect.firstChild);
        ollamaModelSelect.value = currentModel;
      }

    } catch (err) {
      ollamaModelSelect.innerHTML = '';
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = `⚠ Connection error: ${err.message}`;
      ollamaModelSelect.appendChild(opt);
    } finally {
      ollamaRefreshBtn.classList.remove('spinning');
      ollamaRefreshBtn.disabled = false;
    }
  }

  ollamaRefreshBtn?.addEventListener('click', () => {
    fetchOllamaModels(ollamaModelSelect?.value);
  });

  // ── Detect active provider from loaded settings ───────────
  function detectProvider(settings) {
    if (settings.USE_LOCAL_LLM === true || settings.USE_LOCAL_LLM === 'true') return 'ollama';
    if (settings.CEREBRAS_API_KEY) return 'cerebras';
    if (settings.GROQ_API_KEY)     return 'groq';
    if (settings.GITHUB_TOKEN)     return 'github';
    return 'ollama'; // default
  }

  // ── Load settings from API ────────────────────────────────
  async function loadSettings() {
    try {
      const res = await fetch('/api/settings');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const s = data.settings || {};

      // Populate individual fields
      setValue('ollama-url',      s.OLLAMA_BASE_URL);
      setValue('cerebras-key',    s.CEREBRAS_API_KEY);
      setValue('cerebras-model',  s.CEREBRAS_MODEL);
      setValue('groq-key',        s.GROQ_API_KEY);
      setValue('groq-model',      s.GROQ_MODEL);
      setValue('github-token',    s.GITHUB_TOKEN);
      setValue('github-model',    s.GITHUB_QUALITY_MODEL);
      if (portEl) portEl.textContent = s.FLASK_PORT || '5000';

      // Select correct provider radio
      const provider = detectProvider(s);
      providerRadios.forEach(r => {
        r.checked = r.value === provider;
      });
      showProviderFields(provider);

      // Fetch Ollama models and select the current one
      if (provider === 'ollama') {
        fetchOllamaModels(s.OLLAMA_MODEL);
      } else {
        // Still set a placeholder with the current configured model
        if (ollamaModelSelect && s.OLLAMA_MODEL) {
          ollamaModelSelect.innerHTML = '';
          const opt = document.createElement('option');
          opt.value = s.OLLAMA_MODEL;
          opt.textContent = s.OLLAMA_MODEL;
          ollamaModelSelect.appendChild(opt);
          ollamaModelSelect.value = s.OLLAMA_MODEL;
        }
      }
    } catch (err) {
      setHint(`Could not load settings: ${err.message}`, 'error');
    }
  }

  function setValue(id, value) {
    const el = document.getElementById(id);
    if (el && value !== undefined && value !== null) {
      el.value = String(value);
    }
  }

  // ── Open / Close ──────────────────────────────────────────
  function openSettings() {
    overlay.classList.add('open');
    overlay.setAttribute('aria-hidden', 'false');
    openBtn.setAttribute('aria-expanded', 'true');
    clearHint();
    loadSettings();
    // Focus the close button for accessibility
    setTimeout(() => closeBtn?.focus(), 350);
  }

  function closeSettings() {
    overlay.classList.remove('open');
    overlay.setAttribute('aria-hidden', 'true');
    openBtn.setAttribute('aria-expanded', 'false');
    openBtn.focus();
  }

  openBtn.addEventListener('click', openSettings);
  closeBtn?.addEventListener('click', closeSettings);

  // Close on overlay backdrop click
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeSettings();
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('open')) {
      closeSettings();
    }
  });

  // ── Hint helpers ──────────────────────────────────────────
  function setHint(msg, type = '') {
    if (!hint) return;
    hint.textContent = msg;
    hint.className = `settings-hint ${type}`;
  }

  function clearHint() {
    if (!hint) return;
    hint.textContent = '';
    hint.className = 'settings-hint';
  }

  // ── Save settings via POST ────────────────────────────────
  saveBtn?.addEventListener('click', async () => {
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving…';
    clearHint();

    // Determine selected provider to set USE_LOCAL_LLM
    const selectedProvider = [...providerRadios].find(r => r.checked)?.value || 'ollama';
    const useLocalLLM = selectedProvider === 'ollama' ? 'true' : 'false';

    // Read Ollama model from the select dropdown
    const ollamaModel = ollamaModelSelect?.value?.trim() || '';

    const payload = {
      USE_LOCAL_LLM:        useLocalLLM,
      OLLAMA_BASE_URL:      getVal('ollama-url'),
      OLLAMA_MODEL:         ollamaModel,
      CEREBRAS_API_KEY:     getVal('cerebras-key'),
      CEREBRAS_MODEL:       getVal('cerebras-model'),
      GROQ_API_KEY:         getVal('groq-key'),
      GROQ_MODEL:           getVal('groq-model'),
      GITHUB_TOKEN:         getVal('github-token'),
      GITHUB_QUALITY_MODEL: getVal('github-model'),
    };

    // Strip empty values so we don't overwrite existing keys with blanks
    const filtered = Object.fromEntries(
      Object.entries(payload).filter(([, v]) => v.trim() !== '')
    );
    // Always include USE_LOCAL_LLM
    filtered.USE_LOCAL_LLM = useLocalLLM;

    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filtered),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        throw new Error(data.error || `HTTP ${res.status}`);
      }
      setHint('✓ Settings saved. LLM changes take effect on the next request.', 'success');
    } catch (err) {
      setHint(`✗ Failed to save: ${err.message}`, 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save Settings';
    }
  });

  function getVal(id) {
    return document.getElementById(id)?.value?.trim() ?? '';
  }
})();
