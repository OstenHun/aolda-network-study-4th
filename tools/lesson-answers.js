(() => {
  const button = document.querySelector('#download-answers');
  if (!button) return;
  document.body.classList.add('js-ready');
  const fields = [...document.querySelectorAll('textarea[data-answer]')];
  const saved = document.querySelector('#confirm-saved');
  let dirty = false;
  const markDirty = () => { dirty = true; saved.disabled = true; };
  fields.forEach(field => field.addEventListener('input', markDirty));
  const checks = [...document.querySelectorAll('article input[type="checkbox"]')];
  checks.forEach(box => box.addEventListener('change', markDirty));
  window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
  saved.addEventListener('click', () => {
    dirty = false;
    saved.disabled = true;
    document.querySelector('#download-status').textContent = '저장 확인을 기록했습니다. 내용을 더 바꾸면 다시 내려받으세요.';
  });
  button.addEventListener('click', () => {
    const recordSummary = '작성자의 개인 답안이다. 직접 수행·제공 예제·미수행은 작성자가 구분해 적고, 빈칸은 미작성으로 남긴다.';
    const lines = ['# ' + document.title.replace(/ · 실습으로 배우는 네트워크$/, '') + ' — 내 기록', '', '요약: ' + recordSummary, '', '작성일: ' + new Date().toLocaleDateString('ko-KR'), ''];
    fields.forEach(field => lines.push('## ' + field.dataset.answer, '', field.value.trim() || '미작성', ''));
    if (checks.length) { lines.push('## 완료 확인', ''); checks.forEach(box => lines.push('- [' + (box.checked ? 'x' : ' ') + '] ' + box.closest('li')?.textContent.trim())); lines.push(''); }
    const blob = new Blob([lines.join('\n')], {type:'text/markdown;charset=utf-8'});
    const link = document.createElement('a'); link.href = URL.createObjectURL(blob);
    link.download = document.body.dataset.page.replace('.html', '') + '-my-answers.md';
    link.click(); setTimeout(() => URL.revokeObjectURL(link.href), 60000);
    saved.disabled = false;
    document.querySelector('#download-status').textContent = '다운로드를 요청했습니다. 브라우저 다운로드 목록과 저장된 파일을 열어 내용을 확인하세요.';
  });
})();
