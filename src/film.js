import './film.css';
import * as THREE from 'three';
import { createIcons,Play,Pause,Download } from 'lucide';
import { FILM,SHOTS,filmFrame } from './film-timeline.js';
import { createFilmScene } from './film-scene.js';

const $=selector=>document.querySelector(selector);
const icons={Play,Pause,Download};
createIcons({icons});
const canvas=$('#film-canvas');
const context=canvas.getContext('2d',{alpha:false});
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(1);
renderer.setSize(FILM.width,FILM.height,false);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1;
renderer.localClippingEnabled=true;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const camera=new THREE.PerspectiveCamera(58,FILM.width/FILM.height,.035,300);
let world;
let time=.75;
let playing=false;
let exporting=false;
let frameState=null;
let exportProgress=0;
let exportError=null;
let lastExport=null;
let collisionAudit=[];
let lastTimestamp=performance.now();
const format=value=>`${String(Math.floor(value/60)).padStart(2,'0')}:${String(Math.floor(value%60)).padStart(2,'0')}`;
const status=text=>{$('#film-status').textContent=text;};

function render(seconds) {
  if(!world)return;
  time=Math.max(0,Math.min(FILM.duration,seconds));
  frameState=filmFrame(time);
  camera.position.fromArray(frameState.position);
  camera.quaternion.fromArray(frameState.quaternion);
  camera.fov=frameState.fov;
  camera.updateProjectionMatrix();
  world.update(frameState);
  renderer.render(world.scene,camera);
  context.drawImage(renderer.domElement,0,0);
  context.fillStyle='rgba(18,32,25,.66)';
  context.fillRect(0,FILM.height-116,FILM.width,116);
  context.fillStyle='#bfd9c4';
  context.font='500 15px "Helvetica Neue",sans-serif';
  context.fillText(frameState.chapter,54,FILM.height-76);
  context.fillStyle='#f4f7f2';
  context.font='500 28px "PingFang SC",sans-serif';
  context.fillText(frameState.caption,54,FILM.height-34);
  context.textAlign='right';
  context.font='500 16px "Helvetica Neue",sans-serif';
  context.fillStyle='#d7e5d9';
  context.fillText('METRO ATELIER / M01',FILM.width-54,FILM.height-37);
  context.textAlign='left';
  if(frameState.fade>0){
    context.fillStyle=`rgba(0,0,0,${frameState.fade})`;
    context.fillRect(0,0,FILM.width,FILM.height);
  }
  $('#film-time').textContent=`${format(time)} / ${format(FILM.duration)}`;
  $('#film-seek').value=String(time);
}
function setPlaying(value) {
  playing=value;
  $('#film-play').setAttribute('aria-label',value?'暂停':'播放');
  $('#film-play').title=value?'暂停':'播放';
  $('#film-play').innerHTML=`<i data-lucide="${value?'pause':'play'}"></i>`;
  createIcons({icons});
  lastTimestamp=performance.now();
}
function tick(now) {
  requestAnimationFrame(tick);
  if(playing&&!exporting&&world){
    const delta=(now-lastTimestamp)/1000;
    render(time+delta);
    if(time>=FILM.duration)setPlaying(false);
  }
  lastTimestamp=now;
}
requestAnimationFrame(tick);
$('#film-play').onclick=()=>{
  if(!world||exporting)return;
  if(time>=FILM.duration||time<1)render(0);
  setPlaying(!playing);
};
$('#film-seek').oninput=event=>{
  if(exporting)return;
  setPlaying(false);render(Number(event.target.value));
};

async function exportMP4({end=FILM.duration,name='metro-storyboard-preview.mp4'}={}) {
  if(!world||exporting)return;
  exporting=true;exportProgress=0;exportError=null;
  setPlaying(false);
  $('#film-play').disabled=true;$('#film-seek').disabled=true;$('#film-export').disabled=true;
  let output;
  try {
    if(!window.VideoEncoder)throw new Error('当前浏览器不支持 WebCodecs');
    status('正在准备 MP4 编码器');
    const {Output,Mp4OutputFormat,BufferTarget,CanvasSource,Quality}=await import('mediabunny');
    const target=new BufferTarget();
    output=new Output({target,format:new Mp4OutputFormat({fastStart:'in-memory'})});
    const source=new CanvasSource(canvas,{
      codec:'avc',quality:new Quality({bitrate:6_000_000,bitrateMode:'variable'}),
      keyFrameInterval:2,latencyMode:'quality',
    });
    output.addVideoTrack(source,{frameRate:FILM.fps});
    output.setMetadataTags({title:'Metro Atelier / M01 Storyboard Preview'});
    await output.start();
    const total=Math.round(end*FILM.fps);
    for(let index=0;index<total;index++){
      render(index/FILM.fps);
      await source.add(index/FILM.fps,1/FILM.fps,{keyFrame:index%(FILM.fps*2)===0});
      exportProgress=(index+1)/total;
      status(`正在导出 MP4 · ${Math.round(exportProgress*100)}%`);
      if(index%4===0)await new Promise(requestAnimationFrame);
    }
    source.close();
    await output.finalize();
    const blob=new Blob([target.buffer],{type:'video/mp4'});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;link.download=name;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),30000);
    status('MP4 已生成');
    lastExport={bytes:blob.size,frames:total,duration:total/FILM.fps,name};
    return lastExport;
  } catch(error) {
    exportError=error.message;
    status(`导出失败：${error.message}`);
    console.error(error);
    return null;
  } finally {
    if(output&&!['finalized','canceled'].includes(output.state))await output.cancel();
    exporting=false;
    $('#film-play').disabled=false;$('#film-seek').disabled=false;$('#film-export').disabled=false;
  }
}
$('#film-export').onclick=()=>exportMP4();

function auditCameraPath() {
  const raycaster=new THREE.Raycaster();
  const axes=[new THREE.Vector3(1,0,0),new THREE.Vector3(-1,0,0),
    new THREE.Vector3(0,1,0),new THREE.Vector3(0,-1,0),
    new THREE.Vector3(0,0,1),new THREE.Vector3(0,0,-1)];
  const hits=[];
  for(let t=42;t<67;t+=.125){
    const state=filmFrame(t);
    world.update(state);world.scene.updateMatrixWorld(true);
    const meshes=[];
    world.trainRoot.traverse(object=>{
      if(object.isMesh&&object.visible&&!object.material.transparent)meshes.push(object);
    });
    for(const axis of axes){
      raycaster.set(new THREE.Vector3(...state.position),axis);
      raycaster.near=0;raycaster.far=.055;
      const hit=raycaster.intersectObjects(meshes,false)[0];
      if(hit){hits.push({time:Number(t.toFixed(3)),distance:hit.distance});break;}
    }
  }
  collisionAudit=hits;
  render(time);
  return hits;
}
window.film={
  ready:false,
  seek:seconds=>{setPlaying(false);render(seconds);return frameState;},
  exportMP4,
  auditCameraPath,
  diagnostics:()=>({
    ready:!!world,time,phase:frameState?.phase,playing,exporting,exportProgress,exportError,lastExport,
    camera:frameState?.position,trainX:frameState?.trainX,doorAmount:frameState?.doorAmount,
    rearDoor:frameState?.rearDoor,stationAlpha:frameState?.stationAlpha,
    rearPanels:world?.rearPanels.length,wheelGroups:world?.wheels.size,
    collisionAudit,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,
  }),
  timeline:()=>({
    ...FILM,shots:SHOTS,
    frames:Array.from({length:FILM.duration*FILM.fps},(_,index)=>filmFrame(index/FILM.fps)),
  }),
};
try {
  world=await createFilmScene(renderer);
  await document.fonts.ready;
  window.film.ready=true;
  render(time);
  status('');
  $('#film-play').disabled=false;$('#film-seek').disabled=false;$('#film-export').disabled=false;
} catch(error) {
  status(`场景加载失败：${error.message}`);
  console.error(error);
  throw error;
}
