// Front-end de upload e resumo
(function () {
  const fileInput = document.getElementById('fileInput');
  const dropzone = document.getElementById('dropzone');
  const checkImg = document.getElementById('check-img');
  const erroImg = document.getElementById('erro-img');
  const msgErro = document.getElementById('msg-erro');
  const nomeArquivoSpan = document.getElementById('nome-arquivo');
  const textoArraste = document.getElementById('texto-arraste');
  const voltar = document.getElementById('voltar');

  function isPDF(file) {
    if (!file) return false;
    const byType = file.type === 'application/pdf';
    const byExt = file.name.toLowerCase().endsWith('.pdf');
    return byType || byExt;
  }

  function resetUI() {
    if (checkImg) checkImg.style.display = 'none';
    if (erroImg) erroImg.style.display = 'none';
    if (msgErro) msgErro.style.display = 'none';
    if (nomeArquivoSpan) nomeArquivoSpan.textContent = '';
    if (textoArraste) textoArraste.textContent = 'ARRASTE AQUI';
  }

  async function enviarArquivo(file) {
    if (!isPDF(file)) {
      if (erroImg) erroImg.style.display = 'inline-block';
      if (msgErro) {
        msgErro.textContent = 'Formato inválido';
        msgErro.style.display = 'block';
      }
      if (nomeArquivoSpan) nomeArquivoSpan.textContent = file ? file.name : '';
      if (checkImg) checkImg.style.display = 'none';
      return;
    }

    // apenas mostra o nome do arquivo, sem alterar botão nem mostrar telinha
    if (erroImg) erroImg.style.display = 'none';
    if (msgErro) msgErro.style.display = 'none';
    if (checkImg) checkImg.style.display = 'none';
    if (nomeArquivoSpan) nomeArquivoSpan.textContent = file.name;

    const form = new FormData();
    form.append('arquivo', file);

    try {
      const resp = await fetch('/resumir', {
        method: 'POST',
        body: form
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data && data.erro ? data.erro : 'Erro ao processar');
      }
      if (data.redirect) {
        window.location.href = data.redirect;
      } else {
        throw new Error('Resposta inesperada do servidor.');
      }
    } catch (e) {
      if (textoArraste) textoArraste.textContent = 'Falha no envio';
      if (msgErro) { msgErro.textContent = e.message; msgErro.style.display = 'block'; }
      if (checkImg) checkImg.style.display = 'none';
      if (erroImg) erroImg.style.display = 'inline-block';
    }
  }

  // Input por clique
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      resetUI();
      const file = e.target.files && e.target.files[0];
      if (file) enviarArquivo(file);
    });
  }

  // Drag & Drop
  if (dropzone) {
    ['dragenter','dragover'].forEach(evt =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault(); e.stopPropagation();
        dropzone.classList.add('dragover');
      })
    );
    ['dragleave','drop'].forEach(evt =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault(); e.stopPropagation();
        dropzone.classList.remove('dragover');
      })
    );
    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      resetUI();
      if (files && files.length) enviarArquivo(files[0]);
    });
  }

  if (voltar) {
    voltar.addEventListener('click', () => {
      if (document.referrer) {
        history.back();
      } else {
        window.location.href = '/';
      }
    });
  }
})();
