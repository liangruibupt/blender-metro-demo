import './style.css';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { createIcons, Camera, Maximize, Download, Rotate3d, DoorOpen, Layers2, Focus, TrainFront, Armchair, Gauge, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Plus, X, MapPin, ArrowDownToLine, Film, Box } from 'lucide';
import { resolveMove, inDoorway, visitorArea } from './navigation.js';
import { ORBIT_LIMITS, inspectionView, inspectionLayers, inspectionMeshRole } from './inspection.js';
import metroUrl from '../assets/metro.glb?url';
import stationUrl from '../assets/station.glb?url';

const $ = (selector) => document.querySelector(selector);
$('#download-model').href=metroUrl;
const icons = { Camera, Maximize, Download, Rotate3d, DoorOpen, Layers2, Focus, TrainFront, Armchair, Gauge, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Plus, X, MapPin, ArrowDownToLine, Film, Box };
const refreshIcons = () => createIcons({ icons, attrs: { 'stroke-width': 1.6 } });
refreshIcons();
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true });
} catch (error) {
  showError('当前浏览器无法启动 WebGL，请启用硬件加速，或使用 Safari / Chrome。');
  throw error;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
renderer.setClearColor(0xedf0ef);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
$('#viewport').append(renderer.domElement);
renderer.domElement.setAttribute('aria-label', 'M01 三维模型');
renderer.domElement.tabIndex = 0;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xedf0ef);
scene.fog = new THREE.Fog(0xedf0ef, 140, 350);
const camera = new THREE.PerspectiveCamera(38, 1, .035, 400);
const pmrem = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
const environment = pmrem.fromScene(room, .04);
scene.environment = environment.texture;
scene.environmentIntensity = .62;
room.dispose();
pmrem.dispose();
scene.add(new THREE.HemisphereLight(0xf4faf9, 0x82948b, 1.15));
const sun = new THREE.DirectionalLight(0xfffcf0, 3.3);
sun.position.set(8, 17, 11);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -29, right: 29, top: 29, bottom: -29, near: .5, far: 80 });
sun.shadow.normalBias = .026;
sun.shadow.bias = -.0001;
sun.shadow.radius = 3;
scene.add(sun);
const fill = new THREE.DirectionalLight(0xd9eeff, 1.7);
fill.position.set(-7, 8, -12);
scene.add(fill);
const undersideLight = new THREE.DirectionalLight(0xe7f2f0,2.6);
undersideLight.position.set(-8,-18,10);
undersideLight.visible = false;
scene.add(undersideLight);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(350, 350), new THREE.MeshStandardMaterial({ color: 0xe7ebe7, roughness: .95 }));
ground.rotation.x = -Math.PI/2;
ground.position.y = -.32;
ground.receiveShadow = true;
scene.add(ground);
const grid = new THREE.GridHelper(120, 120, 0xcbd4cc, 0xdbe1da);
grid.position.y = -.317;
grid.material.transparent = true;
grid.material.opacity = .23;
scene.add(grid);
grid.visible = false;

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = .065;
Object.assign(controls,ORBIT_LIMITS);
controls.minDistance = 3;
controls.maxDistance = 100;
controls.autoRotateSpeed = .35;
controls.enablePan = true;
controls.target.set(0, 1.6, 0);
let mode = 'platform';
let ready = false;
let autoRotate = false;
let doorOpen = true;
let cutaway = false;
let doorAmount = 0;
let transition = null;
let yaw = Math.PI/2;
let pitch = -.03;
let dragging = null;
let pointerWalk = null;
let activeDetail = null;
let overviewScope = 'station';
let bottomView = false;
let lastLayerKey = '';
const keys = new Set();
const doors = [];
const roof = new THREE.Group();
roof.name = 'Removable roof';
scene.add(roof);
const station = new THREE.Group();
station.name = 'Central station';
scene.add(station);
const stationCover = new THREE.Group();
stationCover.name = 'Station vault and near facade';
scene.add(stationCover);
const trainRoot = new THREE.Group();
trainRoot.name = 'Train body';
scene.add(trainRoot);
const trainTrack = new THREE.Group();
trainTrack.name = 'Train presentation track';
scene.add(trainTrack);
const stationFoundation = new THREE.Group();
stationFoundation.name = 'Station presentation foundation';
scene.add(stationFoundation);
const stationDeck = new THREE.Group();
stationDeck.name = 'Opaque station deck and ballast';
scene.add(stationDeck);
const trainBed = new THREE.Group();
trainBed.name = 'Opaque train display trackbed';
scene.add(trainBed);
const stationXray = new THREE.Group();
stationXray.name = 'Transparent platform reference';
stationXray.visible = false;
scene.add(stationXray);
const inspectionGroups = {
  roof, stationCover, trainTrack, foundation: stationFoundation,
  stationDeck, trainBed,
};

function addPlatformReference(geometry) {
  geometry.computeBoundingBox();
  const size = geometry.boundingBox.getSize(new THREE.Vector3());
  const center = geometry.boundingBox.getCenter(new THREE.Vector3());
  const volume = new THREE.BoxGeometry(size.x,size.y,size.z);
  const outline = new THREE.LineSegments(
    new THREE.EdgesGeometry(volume),
    new THREE.LineBasicMaterial({color:0x578678,transparent:true,opacity:.5,depthWrite:false}),
  );
  volume.dispose();
  outline.position.copy(center);
  stationXray.add(outline);
  // One faint plane avoids stacking hundreds of translucent floor tiles, while
  // keeping rail and train geometry visible through the platform footprint.
  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(size.x,size.z),
    new THREE.MeshBasicMaterial({color:0x73a292,transparent:true,opacity:.045,depthWrite:false,side:THREE.DoubleSide}),
  );
  plane.rotation.x=-Math.PI/2;
  plane.position.set(center.x,geometry.boundingBox.max.y,center.z);
  stationXray.add(plane);
}

const viewpoints = {
  exterior: { number: '01 / 04', name: '站台全景', en: 'STATION OVERVIEW', position: [31, 29, 39], target: [0, 1.65, 4.8] },
  platform: { number: '02 / 04', name: '中央站 · 1 号站台', en: 'CENTRAL / PLATFORM 01', position: [12.4, 2.90, 3.75], target: [-5, 2.45, 1.05] },
  interior: { number: '03 / 04', name: '乘客车厢', en: 'PASSENGER SALOON', position: [-7.70, 2.70, 0], target: [6.7, 2.42, 0] },
  cab: { number: '04 / 04', name: '驾驶室', en: 'DRIVER CAB', position: [7.75, 2.72, .18], target: [9.12, 2.05, 0] },
};
const details = [
  { id:'boarding',modes:['platform','exterior'],label:'登车口',anchor:[-.5,2.30,1.58],view:'platform',index:'01 / BOARDING',title:'站台与车厢',copy:'列车停靠中央站 1 号站台，站台侧车门打开。黄色触觉警示带与深色安全线标识候车边界。',specs:[['列车','M01'],['站台','01 / Harbor Line']],position:[-.5,2.80,2.7],target:[-.5,2.55,0]},
  { id:'departures',modes:['platform'],label:'到站信息',anchor:[6.0,4.28,3.27],view:'platform',index:'02 / DEPARTURES',title:'Harbor Line 到站信息',copy:'悬挂式双面屏区分线路、目的地和预计到站时间，配合出口指示覆盖站台两个来向。屏幕内容为概念静态信息。',specs:[['本站','Central'],['后续列车','Airport / 04 min']],position:[8.9,2.90,3.3],target:[6.0,4.25,3.27]},
  { id:'network',modes:['platform'],label:'线路图',anchor:[3.25,3.12,5.5],view:'platform',index:'03 / NETWORK',title:'中央站换乘线路图',copy:'独立灯箱展示原创三线换乘图；中央站作为换乘节点。背面为城市主题图形，旁边布置候车座椅。',specs:[['线路','Harbor / Park / Airport'],['站台长度','36 m']],position:[3.25,2.80,3.7],target:[3.25,3.16,5.50]},
  { id:'platform',modes:['exterior'],label:'进入站台',anchor:[-10,1.35,3.75],view:'platform',index:'04 / CENTRAL',title:'中央站岛式站台',copy:'双侧轨道围绕连续岛式站台，拱形顶棚、立柱与灯带形成清晰的空间节奏。',specs:[['站台','36 x 6.22 m'],['轨道','双侧布置']],position:[12.4,2.90,3.75],target:[-5,2.45,1.05]},
  { id: 'cab', modes: ['exterior'], label: '驾驶室', anchor: [8.5, 3.18, 0], view: 'cab', index: '01 / DRIVER CAB', title: '面向城市的驾驶视野', copy: '宽幅前风挡、双侧主控制器与三联仪表屏。操纵台下方保留脚踏控制及设备空间。', specs: [['布局', '单人驾驶'], ['仪表', '速度 / 车门 / ATP']], position: [7.75,2.72,.18], target:[9.12,2.05,0] },
  { id: 'saloon', modes: ['exterior'], label: '乘客车厢', anchor: [-1.8, 2.8, 1.5], view: 'interior', index: '02 / SALOON', title: '连续开放的乘客空间', copy: '纵向座椅释放中央通道。立柱、连续扶手与吊环形成不同高度的抓握点。', specs: [['固定座椅', '20 席'], ['折叠座椅', '4 席']], position: [-7.70,2.70,0], target: [6.7,2.42,0] },
  { id: 'bogie', modes: ['exterior'], label: '转向架', anchor: [6.35,.53,1.2], view:'exterior', index:'03 / RUNNING GEAR',title:'双轴转向架',copy:'轮对、轴箱、空气弹簧与构架分层建模。车底布置独立设备箱与散热构件。',specs:[['转向架','2 组'],['轮对','4 组']],position:[9.5,2.2,6.3],target:[6.35,.6,0] },
  { id:'seat',modes:['interior'],label:'座椅细节',anchor:[-3.45,1.99,1.04],view:'interior',index:'04 / SEATING',title:'一体式座椅',copy:'青绿色标准座椅搭配暖色优先座。端部透明隔板、竖向扶手与悬空座椅底座保持通透。',specs:[['座椅形式','纵向五联座'],['配色','Jade / Terracotta']],position:[-4.2,2.52,.12],target:[-3.45,1.87,1.14] },
  { id:'route',modes:['interior'],label:'线路信息',anchor:[-.8,3.10,1.32],view:'interior',index:'05 / WAYFINDING',title:'Harbor Line · 01',copy:'门上线路牌与端部到站屏采用统一的青绿色视觉系统。站点与文字均保留为可编辑的 Blender 对象。',specs:[['方向','Central'],['信息层级','线路 / 站点 / 状态']],position:[-1.7,2.7,.10],target:[-.8,3.08,1.34] },
  { id:'instruments',modes:['cab'],label:'仪表台',anchor:[8.77,2.17,0],view:'cab',index:'06 / INSTRUMENTS',title:'三联驾驶仪表',copy:'速度、车门状态与列车保护状态分区显示。模型中的读数为静态概念界面，不连接真实车辆系统。',specs:[['速度','00 km/h'],['状态','ATP NORMAL']],position:[8.13,2.53,.12],target:[8.79,2.10,0] },
  { id:'controller',modes:['cab'],label:'主控制器',anchor:[8.31,2.31,.93],view:'cab',index:'07 / CONTROLS',title:'触手可及的实体控制',copy:'独立主控制手柄与彩色功能按钮，配合司机座椅、扶手、无线电单元及脚踏控制。',specs:[['构成','控制柄 / 按键 / 无线电'],['形态','概念级建模']],position:[8.04,2.62,.42],target:[8.40,2.09,.72] },
];

function showError(message) {
  $('#loading').hidden = true;
  $('#error').hidden = false;
  $('#error-copy').textContent = message;
}
function toast(message) {
  $('#toast').textContent = message;
  $('#toast').classList.add('visible');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => $('#toast').classList.remove('visible'), 2500);
}
$('#retry').onclick = () => location.reload();

// Combine static geometry by material, retaining separate door and roof groups.
// This keeps the editable Blender asset detailed without hundreds of draw calls.
function optimizeModel(root, defaultOutput = scene) {
  root.updateMatrixWorld(true);
  const batches = new Map();
  root.traverse((object) => {
    if (object.userData.slide !== undefined) {
      const group = new THREE.Group();
      group.userData.slide = object.userData.slide;
      group.userData.side = object.userData.side;
      group.name = object.name;
      scene.add(group);
      doors.push(group);
      object.userData.outputGroup = group;
    }
  });
  root.traverse((object) => {
    if (!object.isMesh) return;
    let parent = object.parent;
    const role = inspectionMeshRole(object.name,object.userData.zone);
    let output = role ? inspectionGroups[role] : defaultOutput;
    while (parent) {
      if (parent.userData.outputGroup) { output = parent.userData.outputGroup; break; }
      parent = parent.parent;
    }
    const geometry = object.geometry.clone().applyMatrix4(object.matrixWorld);
    if (object.name === 'Platform_structure') addPlatformReference(geometry);
    if (geometry.index) {
      const unindexed = geometry.toNonIndexed();
      geometry.dispose();
      addGeometry(unindexed);
    } else addGeometry(geometry);
    function addGeometry(geo) {
      for (const key of Object.keys(geo.attributes)) {
        if (key !== 'position' && key !== 'normal') geo.deleteAttribute(key);
      }
      if (!geo.attributes.normal) geo.computeVertexNormals();
      geo.clearGroups();
      const key = output.uuid + object.material.uuid;
      if (!batches.has(key)) batches.set(key, { output, material: object.material, geometries: [] });
      batches.get(key).geometries.push(geo);
    }
  });
  for (const { output, material, geometries } of batches.values()) {
    const geo = mergeGeometries(geometries, false);
    const mesh = new THREE.Mesh(geo, material);
    if (material.name.includes('glass')) {
      material.transparent = true;
      material.opacity = .18;
      material.depthWrite = false;
      material.side = THREE.DoubleSide;
      material.roughness = .15;
    } else {
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      material.side = THREE.DoubleSide;
    }
    output.add(mesh);
    geometries.forEach((g) => g.dispose());
  }
  root.traverse((o) => { if (o.isMesh) o.geometry.dispose(); });
}

const loader = new GLTFLoader();
Promise.all([loader.loadAsync(metroUrl),loader.loadAsync(stationUrl)]).then(([train,environment]) => {
  optimizeModel(train.scene,trainRoot);
  optimizeModel(environment.scene,station);
  // Fill the interior independently of the exterior sun. Lights are intentionally
  // shadow-free so the first-person views remain responsive on mobile hardware.
  for (const x of [-7,-3,1,5,8.1]) {
    const light = new THREE.PointLight(0xfff3d7, 13, 5.8, 2);
    light.position.set(x,3.12,0);
    scene.add(light);
  }
  for (const x of [-14,-7,0,7,14]) {
    for (const z of [2.8,6.8]) {
      const light = new THREE.PointLight(0xfff4de, 22, 10, 2);
      light.position.set(x,5.72,z);
      scene.add(light);
    }
  }
  ready = true;
  $('#loading').hidden = true;
  $('#capture').disabled = false;
  setView('platform', false);
  buildHotspots();
}).catch((error) => {
  console.error(error);
  showError('请确认本地服务正常运行，并且列车与站台模型均已生成。');
});

function exteriorPreset(bottom = false) {
  const view = inspectionView(overviewScope,bottom,$('#app').clientWidth,$('#app').clientHeight);
  controls.maxDistance = view.maxDistance;
  return view;
}
function updateInspectionLayers() {
  const layers = inspectionLayers(mode,overviewScope,camera.position.y);
  ground.visible = layers.ground;
  station.visible = layers.station;
  stationCover.visible = layers.stationCover;
  stationFoundation.visible = layers.foundation;
  trainTrack.visible = layers.trainTrack;
  trainBed.visible = layers.trainBed;
  stationDeck.visible = layers.stationDeck;
  stationXray.visible = layers.stationXray;
  undersideLight.visible = layers.undersideLight;
  bottomView = layers.below;
  const key = `${mode}:${overviewScope}:${bottomView}`;
  if (key !== lastLayerKey) {
    lastLayerKey = key;
    if (mode === 'exterior') {
      const train = overviewScope === 'train';
      $('#view-name').textContent = bottomView ? (train?'列车底盘':'站台底部 · 透视') : (train?'列车全景':'站台全景');
      $('#view-en').textContent = bottomView ? (train?'TRAIN UNDERCARRIAGE':'STATION UNDERSIDE / X-RAY') : (train?'TRAIN OVERVIEW':'STATION OVERVIEW');
    }
    syncButtons();
    updateHotspotVisibility();
  }
}
function moveCamera(position, target, animated = true) {
  const endPosition = new THREE.Vector3(...position);
  const endTarget = new THREE.Vector3(...target);
  if (animated && !reducedMotion) {
    const direction = camera.getWorldDirection(new THREE.Vector3());
    transition = { start: performance.now(), duration: 1050, from: camera.position.clone(), to: endPosition, fromTarget: camera.position.clone().add(direction.multiplyScalar(4)), toTarget: endTarget };
    controls.enabled = false;
  } else {
    transition = null;
    camera.position.copy(endPosition);
    controls.target.copy(endTarget);
    camera.lookAt(endTarget);
    syncLook(endTarget);
    controls.enabled = mode === 'exterior';
  }
}
function syncLook(target) {
  const dir = target.clone().sub(camera.position).normalize();
  yaw = Math.atan2(dir.x,dir.z);
  pitch = Math.asin(THREE.MathUtils.clamp(dir.y,-1,1));
}
function updateViewUI(next) {
  mode = next;
  const view = viewpoints[next];
  $('#view-number').textContent = view.number;
  $('#view-name').textContent = view.name;
  $('#view-en').textContent = view.en;
  document.body.classList.toggle('inside', next !== 'exterior');
  $('#walk-controls').hidden = next === 'exterior';
  $('#orbit').disabled = next !== 'exterior';
  $('#cutaway').disabled = next !== 'exterior';
  $('#bottom-view').disabled = next !== 'exterior';
  $('#inspection-scope').hidden = next !== 'exterior';
  camera.fov = next === 'exterior' ? (innerWidth < 600 ? 46 : 38) : (innerWidth < 600 ? 82 : 76);
  camera.updateProjectionMatrix();
  roof.visible = next !== 'exterior' || !cutaway;
  sun.intensity = next === 'exterior' ? 3.3 : 1.8;
  const inspectingTrain = next === 'exterior' && overviewScope === 'train';
  $('#scene-name').textContent = inspectingTrain ? 'M01' : 'CENTRAL';
  $('#scene-subtitle').textContent = inspectingTrain ? '城市轨道概念列车' : '中央站 · M01 地铁展示';
  const specs = inspectingTrain ? [['19.4','m','列车长度'],['24','席','含折叠座椅'],['06','组','侧门']] : [['36','m','站台长度'],['02','侧','轨道'],['01','号','Harbor Line']];
  specs.forEach(([value,unit,label],index) => {
    $(`#spec-value-${index}`).textContent=value;
    $(`#spec-unit-${index}`).textContent=unit;
    $(`#spec-label-${index}`).textContent=label;
  });
  document.querySelectorAll('[data-scope]').forEach(button=>button.setAttribute('aria-pressed',button.dataset.scope===overviewScope));
  document.querySelectorAll('[data-view]').forEach((button) => {
    const selected = button.dataset.view === next;
    button.classList.toggle('selected', selected);
    button.setAttribute('aria-pressed', selected);
  });
  updateHotspotVisibility();
  lastLayerKey = '';
}
function setView(next, animated = true) {
  if (!ready) return;
  updateViewUI(next);
  const view = viewpoints[next];
  closeDetail();
  // Clear damped orbit deltas before switching to first-person navigation.
  controls.autoRotate = false;
  controls.enableDamping = false;
  controls.update();
  controls.enableDamping = true;
  const preset = next === 'exterior' ? exteriorPreset() : view;
  moveCamera(preset.position, preset.target, animated);
  updateHotspotVisibility();
}
function closeDetail() {
  $('#detail-panel').hidden = true;
  activeDetail = null;
}
function openDetail(detail) {
  setView(detail.view);
  if (detail.id === 'boarding') doorOpen = true;
  activeDetail = detail.id;
  autoRotate = false;
  syncButtons();
  moveCamera(detail.position, detail.target);
  $('#detail-index').textContent = detail.index;
  $('#detail-title').textContent = detail.title;
  $('#detail-copy').textContent = detail.copy;
  $('#detail-specs').replaceChildren(...detail.specs.map(([key,value]) => {
    const row = document.createElement('div');
    const term = document.createElement('dt');
    const definition = document.createElement('dd');
    term.textContent = key;
    definition.textContent = value;
    row.append(term,definition);
    return row;
  }));
  $('#detail-panel').hidden = false;
}
function buildHotspots() {
  for (const detail of details) {
    const button = document.createElement('button');
    button.className = 'hotspot';
    button.title = detail.label;
    button.setAttribute('aria-label', detail.label);
    button.innerHTML = `<span class="hotspot-marker"><i data-lucide="plus"></i></span><span class="hotspot-label"></span>`;
    button.querySelector('.hotspot-label').textContent = detail.label;
    button.addEventListener('click', () => openDetail(detail));
    $('#hotspots').append(button);
    detail.element = button;
  }
  refreshIcons();
  updateHotspotVisibility();
}
function updateHotspotVisibility() {
  for (const detail of details) {
    if (detail.element) detail.element.hidden = !detailIsVisible(detail);
  }
}
function detailIsVisible(detail) {
  if (!detail.modes.includes(mode)) return false;
  if (mode !== 'exterior') return true;
  if (bottomView) return overviewScope === 'train' && detail.id === 'bogie';
  return overviewScope === 'station' || !['boarding','platform'].includes(detail.id);
}
function syncButtons() {
  for (const [id,state] of [['orbit',autoRotate],['doors',doorOpen],['cutaway',cutaway],['bottom-view',bottomView]]) {
    $(`#${id}`).classList.toggle('active',state);
    $(`#${id}`).setAttribute('aria-pressed',state);
  }
}
syncButtons();
document.querySelectorAll('[data-view]').forEach((button) => button.addEventListener('click', () => setView(button.dataset.view)));
document.querySelectorAll('[data-scope]').forEach(button=>button.addEventListener('click',()=>{
  if (!ready) return;
  overviewScope=button.dataset.scope;
  setView('exterior');
}));
$('#orbit').onclick = () => { autoRotate = !autoRotate; syncButtons(); };
$('#bottom-view').onclick = () => {
  if (!ready || mode !== 'exterior') return;
  closeDetail();
  autoRotate=false;
  const preset=exteriorPreset(!bottomView);
  moveCamera(preset.position,preset.target);
  syncButtons();
};
$('#doors').onclick = () => {
  if (!ready) return;
  if (doorOpen && mode !== 'exterior' && inDoorway(camera.position)) {
    toast('请先离开车门区域');
    return;
  }
  doorOpen = !doorOpen;
  syncButtons();
};
$('#cutaway').onclick = () => { if (!ready) return; cutaway = !cutaway; roof.visible = !cutaway; syncButtons(); };
$('#reset').onclick = () => setView(mode);
$('#close-detail').onclick = closeDetail;
$('#fullscreen').onclick = async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else if ($('#app').requestFullscreen) await $('#app').requestFullscreen();
    else toast('此浏览器不支持全屏');
  } catch { toast('此浏览器不支持全屏'); }
};
$('#capture').onclick = () => {
  renderer.render(scene,camera);
  const link = document.createElement('a');
  link.href = renderer.domElement.toDataURL('image/png');
  link.download = mode==='exterior' ? `${overviewScope}-${bottomView?'bottom':'overview'}.png` : `M01-${mode}.png`;
  link.click();
  toast('当前视角已保存');
};
controls.addEventListener('start', () => {
  if (mode === 'exterior') {
    transition = null;
    autoRotate = false;
    syncButtons();
  }
});

// First-person drag-look and a continuous station-to-train visitor route.
renderer.domElement.addEventListener('pointerdown', (event) => {
  if (mode === 'exterior' || !ready || transition) return;
  dragging = { id: event.pointerId, x: event.clientX, y: event.clientY };
  renderer.domElement.setPointerCapture(event.pointerId);
  renderer.domElement.focus({ preventScroll: true });
});
renderer.domElement.addEventListener('pointermove', (event) => {
  if (!dragging || event.pointerId !== dragging.id) return;
  yaw -= (event.clientX-dragging.x)*.004;
  pitch = THREE.MathUtils.clamp(pitch+(event.clientY-dragging.y)*.003, -1.15,1.15);
  dragging.x=event.clientX;
  dragging.y=event.clientY;
});
for (const type of ['pointerup','pointercancel','lostpointercapture']) {
  renderer.domElement.addEventListener(type, () => { dragging = null; });
}
const movementKeys = ['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'];
window.addEventListener('keydown', (event) => {
  if (event.code === 'Escape') closeDetail();
  if (mode === 'exterior' || !movementKeys.includes(event.code) || event.target.closest('input,textarea,select,[contenteditable]')) return;
  keys.add(event.code);
  event.preventDefault();
});
window.addEventListener('keyup', (event) => keys.delete(event.code));
window.addEventListener('blur', () => { keys.clear(); pointerWalk = null; dragging = null; });
document.querySelectorAll('[data-walk]').forEach((button) => {
  button.addEventListener('pointerdown', (event) => {
    pointerWalk=button.dataset.walk;
    button.setPointerCapture(event.pointerId);
    event.preventDefault();
  });
  for (const type of ['pointerup','pointercancel','lostpointercapture']) button.addEventListener(type, () => { pointerWalk = null; });
});
function walk(dt) {
  let forward=(keys.has('KeyW')||keys.has('ArrowUp')||pointerWalk==='forward'?1:0)-(keys.has('KeyS')||keys.has('ArrowDown')||pointerWalk==='back'?1:0);
  let side=(keys.has('KeyD')||keys.has('ArrowRight')||pointerWalk==='right'?1:0)-(keys.has('KeyA')||keys.has('ArrowLeft')||pointerWalk==='left'?1:0);
  if (forward || side) {
    const length=Math.hypot(forward,side);
    forward/=length; side/=length;
    const delta={
      x:(Math.sin(yaw)*forward-Math.cos(yaw)*side)*dt*1.8,
      z:(Math.cos(yaw)*forward+Math.sin(yaw)*side)*dt*1.8,
    };
    const next=resolveMove(camera.position,delta,doorOpen&&doorAmount>.96);
    camera.position.x=next.x;
    camera.position.z=next.z;
    const nextMode=visitorArea(next);
    if (nextMode!==mode) {
      updateViewUI(nextMode);
      closeDetail();
    }
  }
  camera.lookAt(camera.position.x+Math.sin(yaw)*Math.cos(pitch),camera.position.y+Math.sin(pitch),camera.position.z+Math.cos(yaw)*Math.cos(pitch));
}
function resize() {
  const width=$('#app').clientWidth;
  const height=$('#app').clientHeight;
  renderer.setSize(width,height);
  camera.aspect=width/height;
  camera.updateProjectionMatrix();
  if (ready && mode==='exterior' && !activeDetail) {
    camera.fov=innerWidth<600?46:38;
    camera.updateProjectionMatrix();
    const preset=exteriorPreset(bottomView);
    moveCamera(preset.position,preset.target,false);
  }
}
window.addEventListener('resize',resize);
resize();
camera.position.set(...exteriorPreset().position);
camera.lookAt(0,1.5,0);

const projected=new THREE.Vector3();
const clock=new THREE.Clock();
let frames=0;
function animate(now) {
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),.045);
  if (transition) {
    const progress=THREE.MathUtils.clamp((now-transition.start)/transition.duration,0,1);
    const t=progress*progress*(3-2*progress);
    camera.position.lerpVectors(transition.from,transition.to,t);
    const target=new THREE.Vector3().lerpVectors(transition.fromTarget,transition.toTarget,t);
    camera.lookAt(target);
    if (progress===1) {
      controls.target.copy(transition.toTarget);
      syncLook(transition.toTarget);
      transition=null;
      controls.enabled=mode==='exterior';
    }
  } else if (mode==='exterior') {
    controls.autoRotate=autoRotate&&ready;
    controls.update(dt);
  } else walk(dt);
  doorAmount=THREE.MathUtils.damp(doorAmount,doorOpen?1:0,4.5,dt);
  for (const door of doors) {
    const amount=door.userData.side===-1?doorAmount:0;
    door.position.x=door.userData.slide*amount;
    door.position.z=-door.userData.side*.075*Math.min(amount*5,1);
  }
  updateInspectionLayers();
  renderer.render(scene,camera);
  for (const detail of details) {
    if (!detail.element || !detailIsVisible(detail)) continue;
    projected.set(...detail.anchor).project(camera);
    const x=(projected.x*.5+.5)*renderer.domElement.clientWidth;
    const y=(-projected.y*.5+.5)*renderer.domElement.clientHeight;
    const visible=!transition&&projected.z<1&&projected.z>-1&&x>20&&x<innerWidth-45&&y>105&&y<innerHeight-140&&activeDetail!==detail.id;
    detail.element.style.visibility=visible?'visible':'hidden';
    detail.element.style.left=`${x}px`;
    detail.element.style.top=`${y}px`;
  }
  frames++;
}
requestAnimationFrame(animate);
// Read-only diagnostics support repeatable browser QA without driving UI internals.
window.metroDiagnostics=() => ({ ready,mode,overviewScope,bottomView,autoRotate,doorOpen,doorAmount,cutaway,roofVisible:roof.visible,stationVisible:station.visible,stationCoverVisible:stationCover.visible,groundVisible:ground.visible,foundationVisible:stationFoundation.visible,trainTrackVisible:trainTrack.visible,trainBedVisible:trainBed.visible,stationDeckVisible:stationDeck.visible,stationXrayVisible:stationXray.visible,stationXrayObjects:stationXray.children.length,stationDeckBatches:stationDeck.children.length,trainBedBatches:trainBed.children.length,stationBatches:station.children.length,trainBatches:trainRoot.children.length,doors:doors.length,movingDoors:doors.filter(d=>d.userData.side===-1).length,frames,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,camera:camera.position.toArray(),polarAngle:controls.getPolarAngle(),maxPolarAngle:controls.maxPolarAngle,width:renderer.domElement.width,height:renderer.domElement.height,transitioning:!!transition });
