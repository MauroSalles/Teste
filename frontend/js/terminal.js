/**
 * terminal.js — Terminal /cmd interface logic.
 * Extracted from the original script.js and adapted to the new multi-view layout.
 */

const _history = [];
let _historyIndex = -1;

function pushHistory(cmd) {
  if (cmd && _history[_history.length - 1] !== cmd) {
    _history.push(cmd);
  }
  _historyIndex = _history.length;
}

const cmdInput = document.getElementById('cmd');
const outputEl = document.getElementById('output');

if (cmdInput) {
  cmdInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { enviarComando(); return; }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (_historyIndex > 0) {
        _historyIndex--;
        cmdInput.value = _history[_historyIndex];
      }
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (_historyIndex < _history.length - 1) {
        _historyIndex++;
        cmdInput.value = _history[_historyIndex];
      } else {
        _historyIndex = _history.length;
        cmdInput.value = '';
      }
    }
  });
}

function appendOutput(text, isCommand = false) {
  if (!outputEl) return;
  const prefix = isCommand ? '❯ ' : '  ';
  outputEl.textContent += prefix + text + '\n';
  const container = document.getElementById('output-container');
  if (container) container.scrollTop = container.scrollHeight;
}

function clearOutput() {
  if (outputEl) outputEl.textContent = '';
}

async function enviarComando() {
  if (!cmdInput) return;
  const cmd = cmdInput.value.trim();
  if (!cmd) return;
  cmdInput.value = '';
  pushHistory(cmd);
  appendOutput(cmd, true);

  if (cmd === 'limpar') { clearOutput(); return; }

  try {
    const data = await Api.cmd(cmd);
    if (data.resposta === '__LIMPAR__') { clearOutput(); return; }
    appendOutput(data.resposta);
  } catch (err) {
    appendOutput(`Erro: ${err.message}`);
  }
}

window.enviarComando = enviarComando;
