import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createIcons, Camera, Maximize, Box, TrainFront, Rotate3d, Boxes,
  Wrench, Repeat2, Clapperboard, X, SkipBack, Play, Pause, Download, Square } from 'lucide';
import { createOptimusScene } from './optimus-scene.js';
import { DURATION, modeState, filmState, clamp, fitCamera } from './optimus-rig.js';
import modelUrl from '../assets/optimus.glb?url';

const $=selector=>document.querySelector(selector);
$('#op-download').href=modelUrl;
const icons={Camera,Maximize,Box,TrainFront,Rotate3d,Boxes,Wrench,Repeat2,Clapperboard,X,SkipBack,Play,Pause,Download,Square};
const refreshIcons=()=>createIcons({icons,attrs:{'stroke-width':1.65}});
refreshIcons();
const viewport=$('#op-viewport');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=.95;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
viewport.append(renderer.domElement);
renderer.domElement.setAttribute('aria-label','擎天柱三维场景');
const camera=new THREE.PerspectiveCamera(40,1,.04,200);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.075;
controls.minDistance=3;controls.maxDistance=55;
controls.minPolarAngle=.06;controls.maxPolarAngle=Math.PI*.49;
controls.target.set(0,4,0);
let mode='orbit',time=0,playing=false,truck=false,director=true;
let selected=null,exporting=false,cancelExport=false,exportProgress=0,exportError=null,lastExport=null;
let lastTimestamp=performance.now();
let state=modeState(mode,time,truck);
const world=await createOptimusScene(renderer);
const canvas=renderer.domElement;
const format=value=>`${String(Math.floor(value/60)).padStart(2,'0')}:${String(Math.floor(value%60)).padStart(2,'0')}`;
const labels={orbit:'360° 展示',exploded:'拆解爆炸图',assembly:'组装过程',transform:'变形过程',film:'完整运镜'};
const partGroups=[
  ['head','头部与光学组件','01'],
  ['cab_shell','驾驶舱外壳','02'],
  ['grille','格栅与腹部装甲','03'],
  ['left_shoulder','左臂关节链','04'],
  ['right_shoulder','右臂关节链','05'],
  ['pelvis','腰部与底盘','06'],
  ['left_hip','左腿与后轮组','07'],
  ['right_hip','右腿与后轮组','08'],
];
for(const [id,label,index] of partGroups){
  const button=document.createElement('button');
  button.className='op-part';button.dataset.part=id;button.setAttribute('aria-pressed','false');
  const title=document.createElement('span');title.textContent=label;
  const number=document.createElement('span');number.textContent=index;
  button.append(title,number);
  button.onclick=()=>selectPart(selected===id?null:id);
  $('#op-parts').append(button);
}
function selectPart(id) {
  selected=id;world.select(id);
  document.querySelectorAll('[data-part]').forEach(button=>{
    button.setAttribute('aria-pressed',String(button.dataset.part===id));
  });
}
$('#op-clear-selection').onclick=()=>selectPart(null);

function setPlaying(value) {
  playing=value;lastTimestamp=performance.now();
  $('#op-play').innerHTML=`<i data-lucide="${value?'pause':'play'}"></i>`;
  $('#op-play').setAttribute('aria-label',value?'暂停':'播放');
  $('#op-play').title=value?'暂停':'播放';refreshIcons();
}
function applyCamera(frame, aspect=camera.aspect) {
  const bounds=new THREE.Box3().setFromObject(world.model);
  const {position,target}=fitCamera(frame,bounds,aspect,camera.fov);
  camera.position.copy(position);camera.lookAt(target);controls.target.copy(target);
}
function updateUI() {
  $('#op-time').textContent=`${format(time)} / ${format(DURATION[mode])}`;
  $('#op-timeline').value=String(time);
  $('#op-chapter').textContent=`${String(Object.keys(DURATION).indexOf(mode)+1).padStart(2,'0')} / ${mode==='film'?state.chapter:labels[mode]}`;
  $('#op-scene-caption').textContent=state.chapter;
  $('#op-form-label').textContent=state.transform>.99?'TRUCK CONFIGURATION':state.transform>.01?'TRANSFORMATION IN PROGRESS':'ROBOT CONFIGURATION';
  $('#op-joint-count').textContent=`${world.definition.joints.length} JOINTS / ${world.definition.meshCount} PARTS`;
}
function draw() {
  state=modeState(mode,time,truck);
  world.update(state);
  if(director)applyCamera(state);
  else controls.update();
  renderer.render(world.scene,camera);
  updateUI();
}
function resize() {
  if(exporting)return;
  const rect=viewport.getBoundingClientRect();
  renderer.setSize(rect.width,rect.height);
  camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();
  draw();
}
const observer=new ResizeObserver(resize);observer.observe(viewport);
controls.addEventListener('start',()=>{
  if(exporting)return;
  director=false;$('#op-view').value='free';
});
const freeOption=document.createElement('option');freeOption.value='free';freeOption.textContent='自由视角';
$('#op-view').append(freeOption);
function setMode(value,{at=null,autoplay=false}={}) {
  if(exporting)return;
  if(!Object.hasOwn(DURATION,value))throw new Error(`Unknown mode: ${value}`);
  mode=value;time=at===null?(mode==='exploded'?8:0):clamp(at,0,DURATION[mode]);
  director=true;$('#op-view').value='director';
  if(mode!=='orbit')truck=false;
  $('#op-timeline').max=String(DURATION[mode]);
  document.querySelectorAll('[data-mode]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.mode===mode)));
  document.querySelectorAll('[data-form]').forEach(button=>{
    button.setAttribute('aria-pressed',String(button.dataset.form===(truck?'truck':'robot')));
  });
  setPlaying(autoplay);draw();
}
document.querySelectorAll('[data-mode]').forEach(button=>{
  button.onclick=()=>setMode(button.dataset.mode);
});
document.querySelectorAll('[data-form]').forEach(button=>{
  button.onclick=()=>{truck=button.dataset.form==='truck';setMode('orbit');};
});
$('#op-play').onclick=()=>{
  if(time>=DURATION[mode])time=0;
  setPlaying(!playing);
};
$('#op-restart').onclick=()=>{time=0;setPlaying(false);director=true;$('#op-view').value='director';draw();};
$('#op-timeline').oninput=event=>{
  time=Number(event.target.value);setPlaying(false);draw();
};
$('#op-wireframe').onchange=event=>world.setWireframe(event.target.checked);
$('#op-view').onchange=event=>{
  const value=event.target.value;
  director=value==='director';
  if(director){draw();return;}
  if(value==='free')return;
  setPlaying(false);
  const box=new THREE.Box3().setFromObject(world.model);
  const center=box.getCenter(new THREE.Vector3());
  const size=box.getSize(new THREE.Vector3());
  const distance=Math.max(size.y,size.x,size.z)*1.85*Math.max(1,.8/camera.aspect);
  const direction={front:[0,.08,1],side:[1,.12,0],rear:[0,.1,-1],top:[0,1,.001]}[value];
  camera.position.copy(center).addScaledVector(new THREE.Vector3(...direction),distance);
  controls.target.copy(center);camera.lookAt(center);
};
$('#op-fullscreen').onclick=async()=>{
  try {
    if(document.fullscreenElement)await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  } catch(error){$('#op-export-status').textContent=`无法全屏：${error.message}`;}
};
function download(blob,name) {
  const url=URL.createObjectURL(blob);
  const link=document.createElement('a');link.href=url;link.download=name;link.click();
  setTimeout(()=>URL.revokeObjectURL(url),30000);
}
$('#op-capture').onclick=()=>{
  draw();canvas.toBlob(blob=>{if(blob)download(blob,`optimus-${mode}.png`);});
};
canvas.addEventListener('webglcontextlost',event=>{
  event.preventDefault();setPlaying(false);cancelExport=true;
  $('#op-loading').textContent='图形上下文已丢失，请重新载入。';$('#op-loading').hidden=false;$('#op-retry').hidden=false;
});

async function exportMP4() {
  if(exporting){cancelExport=true;return null;}
  exporting=true;cancelExport=false;exportProgress=0;exportError=null;
  const saved={time,mode,truck,director,position:camera.position.clone(),target:controls.target.clone(),pixelRatio:renderer.getPixelRatio(),selected,wireframe:$('#op-wireframe').checked};
  setPlaying(false);controls.enabled=false;selectPart(null);world.setWireframe(false);
  document.querySelectorAll('button,input,select').forEach(element=>{if(element.id!=='op-export')element.disabled=true;});
  $('#op-export').innerHTML='<i data-lucide="square"></i>';$('#op-export').title='取消导出';
  $('#op-export').setAttribute('aria-label','取消导出');refreshIcons();
  const status=$('#op-export-status');
  let output;
  try {
    if(!window.VideoEncoder)throw new Error('当前浏览器不支持 H.264 WebCodecs 编码');
    status.textContent='正在准备编码器';
    const {Output,Mp4OutputFormat,BufferTarget,CanvasSource,Quality}=await import('mediabunny');
    const target=new BufferTarget();
    output=new Output({target,format:new Mp4OutputFormat({fastStart:'in-memory'})});
    const videoCanvas=document.createElement('canvas');videoCanvas.width=1920;videoCanvas.height=1080;
    const context=videoCanvas.getContext('2d',{alpha:false});
    const source=new CanvasSource(videoCanvas,{codec:'avc',quality:new Quality({bitrate:6_000_000,bitrateMode:'variable'}),keyFrameInterval:2});
    output.addVideoTrack(source,{frameRate:24});
    output.setMetadataTags({title:'Optimus Prime / V2 cinematic metal study'});
    // Reserve the caption band outside the rendered scene, not over the feet.
    renderer.setPixelRatio(1);renderer.setSize(1920,990,false);
    camera.aspect=1920/990;camera.updateProjectionMatrix();
    await output.start();
    for(let index=0;index<1920;index++){
      if(cancelExport)throw new Error('已取消导出');
      const frame=filmState(index/24);
      world.update(frame);applyCamera(frame);renderer.render(world.scene,camera);
      context.drawImage(canvas,0,0);
      context.fillStyle='rgba(242,244,246,.92)';context.fillRect(0,990,1920,90);
      context.fillStyle='#292f38';context.font='600 23px "Barlow",sans-serif';context.textAlign='left';
      context.fillText('OPTIMUS PRIME / METAL V2',48,1043);
      context.font='400 21px "PingFang SC",sans-serif';context.textAlign='right';
      context.fillText(frame.chapter,1872,1043);
      await source.add(index/24,1/24,{keyFrame:index%48===0});
      exportProgress=(index+1)/1920;
      status.textContent=`正在导出 1080p MP4 · ${Math.round(exportProgress*100)}%`;
      if(index%4===0)await new Promise(requestAnimationFrame);
    }
    source.close();await output.finalize();
    const blob=new Blob([target.buffer],{type:'video/mp4'});
    download(blob,'optimus-showcase.mp4');
    lastExport={bytes:blob.size,duration:80,frames:1920,width:1920,height:1080,fps:24};
    status.textContent='MP4 已生成';
    return lastExport;
  } catch(error) {
    exportError=error.message;status.textContent=error.message;
    return null;
  } finally {
    try {
      if(output&&!['finalized','canceled'].includes(output.state))await output.cancel();
    } finally {
      exporting=false;controls.enabled=true;
      ({time,mode,truck,director}=saved);
      renderer.setPixelRatio(saved.pixelRatio);
      document.querySelectorAll('button,input,select').forEach(element=>{element.disabled=false;});
      $('#op-export').innerHTML='<i data-lucide="download"></i>';$('#op-export').title='导出 80 秒 MP4';
      $('#op-export').setAttribute('aria-label','导出完整 MP4');refreshIcons();
      selectPart(saved.selected);world.setWireframe(saved.wireframe);
      camera.position.copy(saved.position);controls.target.copy(saved.target);
      resize();
    }
  }
}
$('#op-export').onclick=()=>exportMP4();
function diagnostics() {
  const bounds=new THREE.Box3().setFromObject(world.model);
  const screen=new THREE.Box3();
  for(const x of [bounds.min.x,bounds.max.x]){
    for(const y of [bounds.min.y,bounds.max.y]){
      for(const z of [bounds.min.z,bounds.max.z])screen.expandByPoint(new THREE.Vector3(x,y,z).project(camera));
    }
  }
  return {
    ...world.diagnostics(),mode,time,playing,director,truck,transform:state.transform,
    explosion:state.explosion,assembly:state.assembly,exporting,exportProgress,exportError,lastExport,
    camera:camera.position.toArray(),bounds,screenBounds:screen,
    surfaceGroundClearance:world.surfaceGroundClearance(),
    drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,
  };
}
window.optimus={
  ready:true,setMode,
  seek(value){time=clamp(value,0,DURATION[mode]);setPlaying(false);draw();return state;},
  exportMP4,
  diagnostics,
};
document.querySelectorAll('button,input,select').forEach(element=>{element.disabled=false;});
resize();
function tick(now) {
  requestAnimationFrame(tick);
  if(!exporting){
    if(playing){
      const elapsed=(now-lastTimestamp)/1000*Number($('#op-speed').value);
      time+=elapsed;
      if(time>=DURATION[mode]){
        if(mode==='orbit')time%=DURATION[mode];
        else {time=DURATION[mode];setPlaying(false);}
      }
    }
    draw();
  }
  lastTimestamp=now;
}
requestAnimationFrame(tick);
