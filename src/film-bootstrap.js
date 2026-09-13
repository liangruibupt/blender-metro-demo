const status=document.querySelector('#film-status');
const retry=document.querySelector('#film-retry');
retry.onclick=()=>location.reload();

// Keep startup failures visible even when a dependency cannot be imported.
const timeout=setTimeout(()=>{
  status.textContent='场景加载超时，请检查本地服务后重试。';
  retry.hidden=false;
},45000);

try {
  await import('./film.js');
  retry.hidden=true;
} catch(error) {
  status.textContent=`场景启动失败：${error.message}`;
  retry.hidden=false;
  console.error('Film startup failed',error);
} finally {
  clearTimeout(timeout);
}
