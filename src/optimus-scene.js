import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { bindRig } from './optimus-rig.js';

export async function createOptimusScene(renderer) {
  const scene=new THREE.Scene();
  scene.background=new THREE.Color(0xe8eaec);
  scene.fog=new THREE.Fog(0xe8eaec,40,120);
  const pmrem=new THREE.PMREMGenerator(renderer);
  const room=new RoomEnvironment();
  const environment=pmrem.fromScene(room,.04);
  scene.environment=environment.texture;
  scene.environmentIntensity=.85;
  pmrem.dispose();room.dispose();
  scene.add(new THREE.HemisphereLight(0xffffff,0xa4a6ac,2.0));
  const key=new THREE.DirectionalLight(0xfff5e9,3.8);
  key.position.set(8,15,12);key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);
  Object.assign(key.shadow.camera,{left:-12,right:12,top:15,bottom:-10,near:.1,far:60});
  key.shadow.normalBias=.035;key.shadow.bias=-.00012;
  scene.add(key);
  const rim=new THREE.DirectionalLight(0xdae9ff,2.8);
  rim.position.set(-6,10,-8);scene.add(rim);
  const fill=new THREE.DirectionalLight(0xffffff,1.3);
  fill.position.set(-8,5,7);scene.add(fill);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),
    new THREE.MeshStandardMaterial({color:0xe3e5e7,roughness:.8}));
  ground.rotation.x=-Math.PI/2;ground.position.y=-.065;ground.receiveShadow=true;scene.add(ground);
  const disk=new THREE.Mesh(new THREE.CylinderGeometry(4.45,4.45,.08,96),
    new THREE.MeshStandardMaterial({color:0xd7dadd,metalness:.32,roughness:.52}));
  disk.position.y=-.028;disk.receiveShadow=true;scene.add(disk);
  const tickGeometry=new THREE.BufferGeometry();
  const points=[];
  for(let i=0;i<120;i++){
    const a=i/120*Math.PI*2;
    const length=i%10===0?.18:.075;
    points.push(Math.sin(a)*4.25,.016,Math.cos(a)*4.25,
      Math.sin(a)*(4.25-length),.016,Math.cos(a)*(4.25-length));
  }
  tickGeometry.setAttribute('position',new THREE.Float32BufferAttribute(points,3));
  const ticks=new THREE.LineSegments(tickGeometry,new THREE.LineBasicMaterial({color:0x969ca3}));
  scene.add(ticks);
  const [gltf,response]=await Promise.all([
    new GLTFLoader().loadAsync('./assets/optimus.glb'),
    fetch('./assets/optimus-rig.json'),
  ]);
  if(!response.ok)throw new Error(`关节数据加载失败：HTTP ${response.status}`);
  const definition=await response.json();
  const model=gltf.scene;
  scene.add(model);
  const rig=bindRig(model,definition);
  // Merge only static meshes inside each joint; all articulated pivots survive.
  for(const joint of definition.joints){
    const node=rig.bindings.get(joint.id);
    const meshes=[];
    node.traverse(object=>{
      if(!object.isMesh)return;
      let owner=object.parent;
      while(owner&&!owner.userData.rigId)owner=owner.parent;
      if(owner===node)meshes.push(object);
    });
    node.updateWorldMatrix(true,true);
    const inverse=node.matrixWorld.clone().invert();
    const batches=new Map();
    for(const mesh of meshes){
      const key=mesh.material.uuid;
      if(!batches.has(key))batches.set(key,{material:mesh.material,geometries:[]});
      let geometry=mesh.geometry.clone();
      geometry.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inverse,mesh.matrixWorld));
      if(geometry.index){const next=geometry.toNonIndexed();geometry.dispose();geometry=next;}
      for(const attribute of Object.keys(geometry.attributes)){
        if(!['position','normal'].includes(attribute))geometry.deleteAttribute(attribute);
      }
      geometry.clearGroups();
      batches.get(key).geometries.push(geometry);
      mesh.removeFromParent();mesh.geometry.dispose();
    }
    for(const {material,geometries} of batches.values()){
      const merged=mergeGeometries(geometries,false);
      if(!merged)throw new Error(`无法合并总成：${joint.id}`);
      const mesh=new THREE.Mesh(merged,material.clone());
      mesh.name=`${joint.id} / ${material.name}`;
      mesh.userData.assembly=joint.id;
      mesh.castShadow=true;mesh.receiveShadow=true;
      node.add(mesh);geometries.forEach(geometry=>geometry.dispose());
    }
  }
  const meshes=[];
  model.traverse(object=>{if(object.isMesh)meshes.push(object);});
  let selected=null;
  function select(id) {
    selected=id;
    for(const mesh of meshes){
      let parent=mesh;
      let active=false;
      while(parent){if(parent.userData.rigId===id)active=true;parent=parent.parent;}
      mesh.material.emissive.setHex(active?0x451614:0x000000);
      mesh.material.emissiveIntensity=active?.30:0;
      if(mesh.material.name==='Optic ice blue'){
        mesh.material.emissive.setHex(0x3accff);mesh.material.emissiveIntensity=1.7;
      }
    }
  }
  select(null);
  return {scene,model,rig,definition,meshes,select,
    update(state) {
      rig.apply(state);
      const exploded=state.assembly===null?state.explosion:1-state.assembly;
      disk.visible=exploded<.03;ticks.visible=disk.visible;
    },
    setWireframe(value){for(const mesh of meshes)mesh.material.wireframe=value;},
    diagnostics:()=>({joints:rig.bindings.size,meshes:meshes.length,selected}),
  };
}
