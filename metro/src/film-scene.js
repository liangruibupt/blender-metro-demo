import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import metroUrl from '../assets/metro.glb?url';
import stationUrl from '../assets/station.glb?url';

export async function createFilmScene(renderer) {
  const scene=new THREE.Scene();
  scene.background=new THREE.Color(0xe9eeea);
  scene.fog=new THREE.Fog(0xe9eeea,100,250);
  const pmrem=new THREE.PMREMGenerator(renderer);
  const room=new RoomEnvironment();
  scene.environment=pmrem.fromScene(room,.04).texture;
  scene.environmentIntensity=.60;
  room.dispose();pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xf4faf7,0x7d8c83,1.3));
  const sun=new THREE.DirectionalLight(0xfff7e9,2.4);
  sun.position.set(8,18,12);
  sun.castShadow=true;
  sun.shadow.mapSize.set(2048,2048);
  Object.assign(sun.shadow.camera,{left:-30,right:30,top:30,bottom:-30,near:.5,far:85});
  sun.shadow.normalBias=.024;sun.shadow.bias=-.00012;
  scene.add(sun);
  const fill=new THREE.DirectionalLight(0xd5e6f0,1.1);
  fill.position.set(-8,9,-12);scene.add(fill);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(250,250),
    new THREE.MeshStandardMaterial({color:0xdde5df,roughness:.95}));
  ground.rotation.x=-Math.PI/2;ground.position.y=-.56;ground.receiveShadow=true;scene.add(ground);
  const trainRoot=new THREE.Group();
  const railRoot=new THREE.Group();
  const stationRoot=new THREE.Group();
  const stationCover=new THREE.Group();
  const stationWalls=new THREE.Group();
  const rearDoor=new THREE.Group();
  trainRoot.add(rearDoor);
  scene.add(trainRoot,railRoot,stationRoot,stationCover,stationWalls);
  const doorGroups=[];
  const wheels=new Map();
  const materialCache=new Map();
  const stationMaterials=new Set();
  const stationMeshes=[];
  const clipPlanes=[
    new THREE.Plane(new THREE.Vector3(1,0,0),20.38),
    new THREE.Plane(new THREE.Vector3(-1,0,0),20.38),
  ];
  const loader=new GLTFLoader();
  const [train,station]=await Promise.all([
    loader.loadAsync(metroUrl),
    loader.loadAsync(stationUrl),
  ]);
  function materialFor(source,isTrain,isStation) {
    const key=source.uuid+(isTrain?'train':isStation?'station':'rail');
    if(!materialCache.has(key)){
      const material=source.clone();
      material.side=THREE.DoubleSide;
      if(material.name.toLowerCase().includes('glass')){
        material.transparent=true;material.opacity=.20;material.depthWrite=false;
      }
      if(isTrain){material.clippingPlanes=clipPlanes;material.clipShadows=true;}
      if(isStation)stationMaterials.add(material);
      materialCache.set(key,material);
    }
    return materialCache.get(key);
  }
  function batch(root,isTrainAsset) {
    root.updateMatrixWorld(true);
    const batches=new Map();
    root.traverse(object=>{
      if(object.userData.slide!==undefined){
        const group=new THREE.Group();
        group.userData={slide:object.userData.slide,side:object.userData.side};
        trainRoot.add(group);
        doorGroups.push(group);
        object.userData.filmGroup=group;
      }
    });
    root.traverse(object=>{
      if(!object.isMesh)return;
      // The movie variant replaces the solid rear bulkhead with a real aperture.
      if(isTrainAsset&&object.name==='Rear_bulkhead')return;
      if(isTrainAsset&&object.name==='Cab_LCD_text')return;
      let output=isTrainAsset?trainRoot:stationRoot;
      const isTrack=object.userData.zone==='07_Track';
      if(isTrack)output=railRoot;
      if(object.userData.zone==='10_Station_Cover')output=stationCover;
      if(!isTrainAsset&&object.name.startsWith('Far_wall'))output=stationWalls;
      if(['Rear_end_door','Rear_end_Glass','Rear_door_grip','Rear_car_label'].some(prefix=>object.name.startsWith(prefix)))output=rearDoor;
      let parent=object.parent;
      while(parent){if(parent.userData.filmGroup){output=parent.userData.filmGroup;break;}parent=parent.parent;}
      let geometry=object.geometry.clone().applyMatrix4(object.matrixWorld);
      if(isTrainAsset&&object.name.startsWith('Wheel_')){
        geometry.computeBoundingBox();
        const center=geometry.boundingBox.getCenter(new THREE.Vector3());
        const key=center.x.toFixed(3);
        if(!wheels.has(key)){
          const group=new THREE.Group();
          group.position.set(center.x,.44,0);
          trainRoot.add(group);wheels.set(key,group);
        }
        output=wheels.get(key);
        geometry.translate(-output.position.x,-output.position.y,0);
      }
      if(geometry.index){
        const next=geometry.toNonIndexed();geometry.dispose();geometry=next;
      }
      for(const key of Object.keys(geometry.attributes)){
        if(!['position','normal'].includes(key))geometry.deleteAttribute(key);
      }
      if(!geometry.attributes.normal)geometry.computeVertexNormals();
      geometry.clearGroups();
      const material=materialFor(object.material,isTrainAsset&&!isTrack,!isTrainAsset);
      const key=output.uuid+material.uuid;
      if(!batches.has(key))batches.set(key,{output,material,geometries:[]});
      batches.get(key).geometries.push(geometry);
    });
    for(const {output,material,geometries} of batches.values()){
      const mesh=new THREE.Mesh(mergeGeometries(geometries,false),material);
      mesh.castShadow=!material.transparent;mesh.receiveShadow=true;
      if(!isTrainAsset)stationMeshes.push(mesh);
      output.add(mesh);
      geometries.forEach(geometry=>geometry.dispose());
    }
    root.traverse(object=>{if(object.isMesh)object.geometry.dispose();});
  }
  batch(train.scene,true);batch(station.scene,false);
  const displayCanvas=document.createElement('canvas');
  displayCanvas.width=512;displayCanvas.height=256;
  const displayContext=displayCanvas.getContext('2d');
  const displayTexture=new THREE.CanvasTexture(displayCanvas);
  displayTexture.colorSpace=THREE.SRGBColorSpace;
  const doorDisplay=new THREE.Mesh(new THREE.PlaneGeometry(.56,.225),
    new THREE.MeshBasicMaterial({map:displayTexture,clippingPlanes:clipPlanes}));
  doorDisplay.rotation.y=-Math.PI/2;
  doorDisplay.position.set(8.750,2.15,.77);
  trainRoot.add(doorDisplay);
  let lastDoorDisplay='';
  const wallMaterial=[...materialCache.values()].find(material=>material.name==='Porcelain interior');
  const rearPanels=[];
  for(const [position,size] of [
    [[-9.09,2.34,-.9575],[.12,2.22,.895]],
    [[-9.09,2.34,.9575],[.12,2.22,.895]],
    [[-9.09,3.315,0],[.12,.27,1.02]],
  ]){
    const panel=new THREE.Mesh(new THREE.BoxGeometry(...size),wallMaterial);
    panel.position.set(...position);panel.castShadow=true;panel.receiveShadow=true;
    trainRoot.add(panel);rearPanels.push(panel);
  }
  for(const x of [-7,-3,1,5,8.1]){
    const light=new THREE.PointLight(0xfff4e2,12,5.8,2);
    light.position.set(x,3.12,0);trainRoot.add(light);
  }
  const stationLights=new THREE.Group();
  for(const x of [-14,-7,0,7,14]){
    for(const z of [2.8,6.8]){
      const light=new THREE.PointLight(0xfff5e5,20,10,2);
      light.position.set(x,5.72,z);stationLights.add(light);
    }
  }
  scene.add(stationLights);
  let lastAlpha=-1;
  function update(state) {
    trainRoot.position.x=state.trainX;
    for(const group of doorGroups){
      const amount=group.userData.side===-1?state.doorAmount:0;
      group.position.x=group.userData.slide*amount;
      group.position.z=-group.userData.side*.075*Math.min(amount*5,1);
    }
    for(const group of wheels.values())group.rotation.z=-state.trainX/.4;
    rearDoor.position.z=state.rearDoor*1.08;
    stationRoot.visible=state.stationAlpha>.001;
    stationWalls.visible=state.phase!=='station-orbit'&&state.stationAlpha>.001;
    stationCover.visible=state.cover&&state.stationAlpha>.001;
    stationLights.visible=state.stationAlpha>.5;
    if(state.stationAlpha!==lastAlpha){
      for(const material of stationMaterials){
        const transparent=state.stationAlpha<.999;
        if(material.transparent!==transparent){material.transparent=transparent;material.needsUpdate=true;}
        material.opacity=state.stationAlpha;
        material.depthWrite=!transparent;
      }
      for(const mesh of stationMeshes)mesh.castShadow=state.stationAlpha>.98;
      lastAlpha=state.stationAlpha;
    }
    const doorLabel=state.doorAmount>.01?'OPEN':'CLOSED';
    if(doorLabel!==lastDoorDisplay){
      displayContext.fillStyle='#092b32';displayContext.fillRect(0,0,512,256);
      displayContext.fillStyle='#bdebdc';displayContext.textAlign='center';
      displayContext.font='500 49px "Helvetica Neue",sans-serif';
      displayContext.fillText('DOORS',256,104);
      displayContext.font='500 59px "Helvetica Neue",sans-serif';
      displayContext.fillText(doorLabel,256,185);
      displayTexture.needsUpdate=true;
      lastDoorDisplay=doorLabel;
    }
  }
  return {scene,update,trainRoot,rearDoor,doorGroups,wheels,rearPanels};
}
