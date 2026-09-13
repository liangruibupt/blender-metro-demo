import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { bindRig, bindGuides } from './optimus-rig.js';
import modelUrl from '../assets/optimus.glb?url';
import rigUrl from '../assets/optimus-rig.json?url';

export async function createOptimusScene(renderer) {
  const scene=new THREE.Scene();
  scene.background=new THREE.Color(0x858a91);
  scene.fog=new THREE.Fog(0x858a91,40,120);
  const pmrem=new THREE.PMREMGenerator(renderer);
  const room=new THREE.Scene();
  room.background=new THREE.Color(.075,.085,.105);
  for(const [position,size,color] of [
    [[-5,5,5],[3,9],[5.2,5.8,6.4]],[[6,6,0],[2.3,10],[7.5,7.0,6.5]],
    [[0,10,-1],[8,4],[4.0,4.4,5.4]],[[-4,3,-6],[2,8],[3.0,4.3,6.2]],
  ]){
    const panel=new THREE.Mesh(new THREE.PlaneGeometry(...size),
      new THREE.MeshBasicMaterial({color:new THREE.Color(...color),side:THREE.DoubleSide}));
    panel.position.fromArray(position);panel.lookAt(0,3,0);room.add(panel);
  }
  const environment=pmrem.fromScene(room,.025);
  scene.environment=environment.texture;
  scene.environmentIntensity=1.05;
  pmrem.dispose();
  room.traverse(object=>{if(object.isMesh){object.geometry.dispose();object.material.dispose();}});
  scene.add(new THREE.HemisphereLight(0xe7efff,0x555963,.65));
  const key=new THREE.DirectionalLight(0xfff5e9,3.8);
  key.position.set(8,15,12);key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);
  Object.assign(key.shadow.camera,{left:-12,right:12,top:15,bottom:-10,near:.1,far:60});
  key.shadow.normalBias=.035;key.shadow.bias=-.00012;
  scene.add(key);
  const rim=new THREE.DirectionalLight(0xdae9ff,3.8);
  rim.position.set(-6,10,-8);scene.add(rim);
  const fill=new THREE.DirectionalLight(0xffffff,.9);
  fill.position.set(-8,5,7);scene.add(fill);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),
    new THREE.MeshStandardMaterial({color:0x7b8088,roughness:.78}));
  ground.rotation.x=-Math.PI/2;ground.position.y=-.065;ground.receiveShadow=true;scene.add(ground);
  const disk=new THREE.Mesh(new THREE.CylinderGeometry(4.45,4.45,.08,96),
    new THREE.MeshStandardMaterial({color:0x555e6b,metalness:.6,roughness:.45}));
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
  const ticks=new THREE.LineSegments(tickGeometry,new THREE.LineBasicMaterial({color:0x9fa9b6}));
  scene.add(ticks);
  const [gltf,response]=await Promise.all([
    new GLTFLoader().loadAsync(modelUrl),
    fetch(rigUrl),
  ]);
  if(!response.ok)throw new Error(`关节数据加载失败：HTTP ${response.status}`);
  const definition=await response.json();
  const model=gltf.scene;
  scene.add(model);
  const rig=bindRig(model,definition);
  const guides=bindGuides(model,definition);
  // Merge only static meshes inside each joint; all articulated pivots survive.
  for(const joint of definition.joints){
    const node=rig.bindings.get(joint.id);
    const meshes=[];
    node.traverse(object=>{
      if(!object.isMesh)return;
      let owner=object.parent;
      while(owner&&!owner.userData.rigId){
        if(owner.userData.linkId)return;
        owner=owner.parent;
      }
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
        if(!['position','normal','uv'].includes(attribute))geometry.deleteAttribute(attribute);
      }
      if(!geometry.attributes.uv)geometry.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(geometry.attributes.position.count*2),2));
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
  model.traverse(object=>{
    if(!object.isMesh)return;
    if(!object.userData.assembly)object.material=object.material.clone();
    object.castShadow=true;object.receiveShadow=true;
    object.userData.baseEmission=object.material.emissive.clone();
    object.userData.baseEmissionIntensity=object.material.emissiveIntensity;
    meshes.push(object);
  });
  let selected=null;
  function select(id) {
    selected=id;
    for(const mesh of meshes){
      let parent=mesh;
      let active=false;
      while(parent){if(parent.userData.rigId===id)active=true;parent=parent.parent;}
      mesh.material.emissive.copy(mesh.userData.baseEmission);
      if(active)mesh.material.emissive.add(new THREE.Color(0x35100e));
      mesh.material.emissiveIntensity=active?Math.max(.30,mesh.userData.baseEmissionIntensity):mesh.userData.baseEmissionIntensity;
    }
  }
  select(null);
  function surfaceGroundClearance() {
    model.updateWorldMatrix(true,true);
    let minimum=Infinity;
    for(const mesh of meshes){
      const p=mesh.geometry.attributes.position;
      const e=mesh.matrixWorld.elements;
      for(let index=0;index<p.count;index++){
        minimum=Math.min(minimum,e[1]*p.getX(index)+e[5]*p.getY(index)+e[9]*p.getZ(index)+e[13]);
      }
    }
    return minimum;
  }
  return {scene,model,rig,definition,meshes,select,surfaceGroundClearance,
    update(state) {
      rig.apply(state);
      guides.update(state.transform);
      const exploded=state.assembly===null?state.explosion:1-state.assembly;
      disk.visible=exploded<.03;ticks.visible=disk.visible;
    },
    setWireframe(value){for(const mesh of meshes)mesh.material.wireframe=value;},
    diagnostics:()=>({
      joints:rig.bindings.size,meshes:meshes.length,selected,guides:guides.count,
      texturedMeshes:meshes.filter(mesh=>mesh.material.map&&mesh.geometry.attributes.uv).length,
      normalMappedMeshes:meshes.filter(mesh=>mesh.material.normalMap).length,
      weapons:definition.weapons.map(weapon=>{
        const node=rig.bindings.get(weapon.joint);
        const bounds=new THREE.Box3().setFromObject(node);
        let visible=true;
        for(let parent=node;parent;parent=parent.parent)visible&&=parent.visible;
        return {kind:weapon.kind,joint:weapon.joint,visible,
          meshes:meshes.filter(mesh=>mesh.userData.assembly===weapon.joint).length,
          bounds};
      }),
    }),
  };
}
