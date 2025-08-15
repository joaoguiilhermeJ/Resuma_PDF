function copiarTexto() {
  const area = document.getElementById('resumoTexto');
  area.select();
  area.setSelectionRange(0, 99999);
  document.execCommand('copy');
}

function salvarAlteracoes() {
  const area = document.getElementById('resumoTexto');
  const blob = new Blob([area.value], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'resumo.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
