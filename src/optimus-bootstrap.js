import './optimus.css';
const message=document.querySelector('#op-loading');
const retry=document.querySelector('#op-retry');
retry.onclick=()=>location.reload();
const timeout=setTimeout(()=>{
  message.textContent='场景载入超时，请检查本地服务。';
  retry.hidden=false;
},45000);
try {
  await import('./optimus.js');
  message.hidden=true;retry.hidden=true;
} catch(error) {
  message.textContent=`无法载入场景：${error.message}`;
  message.hidden=false;retry.hidden=false;
  console.error(error);
} finally {
  clearTimeout(timeout);
}
