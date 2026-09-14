import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { Box3, Group, PerspectiveCamera, Quaternion, Euler, Vector3 } from 'three';
import { bindRig, bindGuides, guidePose, jointMatrices, jointPose, filmState, modeState, CHAPTERS, fitCamera } from './optimus-rig.js';

const definition=JSON.parse(readFileSync(new URL('../assets/optimus-rig.json',import.meta.url)));
const near=(a,b,epsilon=1e-7)=>assert.ok(Math.abs(a-b)<epsilon,`${a} != ${b}`);

test('rig has a single parent tree with six wheels and no duplicate joint IDs',()=>{
  const seen=new Set();
  for(const joint of definition.joints){
    assert.ok(!seen.has(joint.id));
    if(joint.parent)assert.ok(seen.has(joint.parent));
    seen.add(joint.id);
  }
  assert.equal(definition.joints.filter(joint=>!joint.parent).length,1);
  assert.equal(definition.joints.filter(joint=>joint.id.includes('wheel')).length,6);
});
test('the real Blender export contains exactly the documented articulated hierarchy',()=>{
  const buffer=readFileSync(new URL('../assets/optimus.glb',import.meta.url));
  assert.equal(buffer.readUInt32LE(0),0x46546c67);
  const gltf=JSON.parse(buffer.subarray(20,20+buffer.readUInt32LE(12)).toString());
  const ids=gltf.nodes.filter(node=>node.extras?.rigId).map(node=>node.extras.rigId).sort();
  assert.deepEqual(ids,definition.joints.map(joint=>joint.id).sort());
});
test('robot and truck use the same joint objects, without scaling or replacing geometry',()=>{
  const model=new Group();
  const nodes=new Map();
  for(const joint of definition.joints){
    const object=new Group();object.userData.rigId=joint.id;
    (nodes.get(joint.parent)||model).add(object);nodes.set(joint.id,object);
  }
  const rig=bindRig(model,definition);
  const objects=[...rig.bindings.values()];
  for(let t=0;t<=1;t+=.01){
    rig.apply({transform:t});
    assert.deepEqual([...rig.bindings.values()],objects);
    for(const object of objects)assert.deepEqual(object.scale.toArray(),[1,1,1]);
  }
});
test('both endpoint poses match the rig definition',()=>{
  for(const joint of definition.joints){
    for(const t of [0,1]){
      const pose=jointPose(joint,{transform:t});
      pose.position.toArray().forEach((value,index)=>near(value,(t?joint.truck:joint.robot)[index]));
      const expected=new Quaternion().setFromEuler(new Euler(...(t?joint.truckAngles:joint.angles)));
      near(pose.quaternion.angleTo(expected),0);
    }
  }
});
test('assembly starts exploded and ends exactly at the robot pose',()=>{
  for(const joint of definition.joints){
    const start=jointPose(joint,{assembly:0});
    const exploded=jointPose(joint,{explosion:1});
    near(start.position.distanceTo(exploded.position),0);
    const end=jointPose(joint,{assembly:1});
    near(end.position.distanceTo(jointPose(joint).position),0);
  }
});
test('the head retracts only while the roof hatch is open',()=>{
  const head=definition.joints.find(joint=>joint.id==='head');
  const roof=definition.joints.find(joint=>joint.id==='right_roof');
  for(let t=.14;t<.36;t+=.01){
    assert.ok(jointPose(roof,{transform:t}).position.x-roof.robot[0]>.80);
    assert.ok(jointPose(head,{transform:t}).position.y<head.robot[1]);
  }
});
test('the chassis follows a sampled ground-contact curve',()=>{
  const chassis=definition.joints.find(joint=>joint.id==='chassis');
  assert.equal(chassis.motion.type,'grounded');
  assert.equal(chassis.motion.heightCurve.length,257);
  assert.ok(chassis.motion.heightCurve.every(Number.isFinite));
  near(chassis.motion.heightCurve[0],chassis.robot[1]);
  near(chassis.motion.heightCurve.at(-1),chassis.truck[1]);
});
test('film covers the four requested presentations and closes on the robot',()=>{
  assert.equal(CHAPTERS[0].start,0);
  assert.equal(CHAPTERS.at(-1).end,80);
  assert.deepEqual([...new Set(CHAPTERS.map(shot=>shot.type))].sort(),
    ['assembly','exploded','orbit','transform']);
  assert.equal(filmState(0).transform,0);
  assert.equal(filmState(60).transform,1);
  assert.equal(filmState(80).transform,0);
});
test('camera and every articulated part move continuously through the entire film',()=>{
  let previous=filmState(0);
  for(let frame=1;frame<=1920;frame++){
    const current=filmState(frame/24);
    for(let axis=0;axis<3;axis++)assert.ok(Math.abs(current.camera[axis]-previous.camera[axis])<1.1);
    for(const joint of definition.joints){
      const a=jointPose(joint,previous);const b=jointPose(joint,current);
      assert.ok(a.position.distanceTo(b.position)<.24,`${joint.id} at ${frame}`);
      assert.ok(a.quaternion.angleTo(b.quaternion)<.08,`${joint.id} rotation at ${frame}`);
    }
    previous=current;
  }
});
test('timeline clamping and all interactive endpoints are deterministic',()=>{
  assert.deepEqual(filmState(-5),filmState(0));
  assert.deepEqual(filmState(95),filmState(80));
  assert.equal(modeState('transform',14).transform,1);
  assert.equal(modeState('exploded',8).explosion,1);
  assert.equal(modeState('assembly',12).assembly,1);
  assert.equal(modeState('orbit',0,true).transform,1);
});
test('intermediate transformation stays in frame on desktop and mobile',()=>{
  const bounds=new Box3(new Vector3(-3,.47,-2.65),new Vector3(3,7.57,1.01));
  for(const aspect of [.63,1.45,16/9]){
    const pose=fitCamera(modeState('transform',7),bounds,aspect);
    const camera=new PerspectiveCamera(40,aspect,.04,200);
    camera.position.copy(pose.position);camera.lookAt(pose.target);camera.updateMatrixWorld(true);
    for(const x of [bounds.min.x,bounds.max.x]){
      for(const y of [bounds.min.y,bounds.max.y]){
        for(const z of [bounds.min.z,bounds.max.z]){
          const projected=new Vector3(x,y,z).project(camera);
          assert.ok(Math.abs(projected.x)<.91);
          assert.ok(Math.abs(projected.y)<.91);
        }
      }
    }
  }
});
test('V3 uses embedded metal/roughness and normal textures with UV coordinates',()=>{
  const buffer=readFileSync(new URL('../assets/optimus.glb',import.meta.url));
  const gltf=JSON.parse(buffer.subarray(20,20+buffer.readUInt32LE(12)).toString());
  assert.equal(definition.version,3);
  assert.ok(gltf.images.length>=13);
  const materials=new Set();
  gltf.materials.forEach((material,index)=>{
    if(material.pbrMetallicRoughness?.metallicRoughnessTexture){
      assert.ok(material.normalTexture);
      materials.add(index);
    }
  });
  assert.ok(materials.size>=6);
  for(const mesh of gltf.meshes){
    for(const primitive of mesh.primitives){
      if(materials.has(primitive.material))assert.ok(primitive.attributes.TEXCOORD_0!==undefined);
    }
  }
});
test('guide stages always overlap and their endpoints track the real joints',()=>{
  const model=new Group(),nodes=new Map(),ends=new Map();
  for(const joint of definition.joints){
    const object=new Group();object.userData.rigId=joint.id;
    (nodes.get(joint.parent)||model).add(object);nodes.set(joint.id,object);
  }
  for(const link of definition.links){
    const group=new Group();group.userData.linkId=link.id;
    nodes.get(link.base).add(group);
    for(let index=0;index<link.stages;index++){
      const stage=new Group();stage.userData.linkStage=index;group.add(stage);
    }
    const end=new Group();end.userData.linkEnd=true;group.add(end);ends.set(link.id,end);
  }
  const rig=bindRig(model,definition),guides=bindGuides(model,definition);
  assert.equal(guides.count,11);
  for(let index=0;index<=160;index++){
    const transform=index/160;
    rig.apply({transform});guides.update(transform);model.updateMatrixWorld(true);
    const frame=jointMatrices(definition.joints,transform);
    for(const link of definition.links){
      const pose=guidePose(link,frame);
      assert.ok(pose.length>=link.stageLength-1e-6,link.id);
      assert.ok((pose.length-link.stageLength)/(link.stages-1)<link.stageLength,link.id);
      const actual=ends.get(link.id).getWorldPosition(new Vector3());
      const target=nodes.get(link.target).localToWorld(new Vector3(...link.end));
      near(actual.distanceTo(target),0,1e-5);
      assert.deepEqual(ends.get(link.id).scale.toArray(),[1,1,1]);
    }
  }
});
test('triangle collision audit is passing and matches the current assets',()=>{
  const report=JSON.parse(readFileSync(new URL('../qa/motion-audit.json',import.meta.url)));
  assert.equal(report.result,'PASS');
  assert.deepEqual(report.grounding.failures,[]);
  assert.ok(report.grounding.bodyMax<.065,'weapons must not lift the body off the floor');
  assert.ok(report.grounding.surfaceMin>=.02,'no weapon may cross the floor');
  assert.equal(Object.keys(report.grounding.truckWheels).length,6);
  for(const clearance of Object.values(report.grounding.truckWheels)){
    assert.ok(clearance>=.02&&clearance<=.07,'all six truck tires must reach the floor');
  }
  assert.ok(report.pairs>=67);
  assert.equal(report.pairs,report.checkedPairs.length);
  assert.ok(report.samples>=161);
  const hash=file=>createHash('sha256').update(readFileSync(new URL(file,import.meta.url))).digest('hex');
  assert.equal(report.assetSha256,hash('../assets/optimus.glb'));
  assert.equal(report.rigSha256,hash('../assets/optimus-rig.json'));
  assert.equal(report.blendSha256,hash('../deliverables/optimus-prime.blend'));
  assert.equal(report.poseEvaluatorSha256,hash('../scripts/rig_motion.py'));
  assert.equal(report.generatorSha256,hash('../scripts/build_optimus.py'));
  assert.equal(report.weaponGeneratorSha256,hash('../scripts/weapons.py'));
});
test('browser poses match the independently evaluated Blender audit poses',()=>{
  const report=JSON.parse(readFileSync(new URL('../qa/motion-audit.json',import.meta.url)));
  assert.equal(report.poseSamples.length,17);
  for(const sample of report.poseSamples){
    for(const joint of definition.joints){
      const actual=jointPose(joint,{transform:sample.transform});
      const expected=sample.joints[joint.id];
      near(actual.position.distanceTo(new Vector3(...expected.position)),0,2e-6);
      near(actual.quaternion.angleTo(new Quaternion(...expected.quaternion).normalize()),0,2e-6);
    }
  }
});
test('rear carriages clear calf sides before crossing depth',()=>{
  for(const side of ['left','right']){
    const joint=definition.joints.find(j=>j.id===`${side}_rear_bogie`);
    assert.ok(joint.robot[2]===0);
    for(let i=1;i<100;i++){
      const p=jointPose(joint,{transform:.14+.14*i/100}).position;
      assert.ok(Math.abs(p.x)>.99);
    }
    near(jointPose(joint,{transform:1}).position.z,2);
    assert.equal(definition.joints.find(j=>j.id===`${side}_rear_wheel_32`).parent,joint.id);
    assert.ok(definition.links.some(link=>link.target===joint.id));
  }
});
test('both reference weapons belong to connected arm mounts and stay present in every mode',()=>{
  assert.deepEqual(definition.weapons.map(weapon=>weapon.kind).sort(),['energon_axe','rifle']);
  for(const weapon of definition.weapons){
    const pivot=definition.joints.find(joint=>joint.id===weapon.joint);
    const mount=definition.joints.find(joint=>joint.id===pivot.parent);
    const hand=definition.joints.find(joint=>joint.id===weapon.hand);
    assert.equal(mount.parent,hand.parent);
    assert.ok(definition.links.some(link=>link.target===mount.id&&link.base===hand.parent));
    for(const time of [0,3,6,9,12]){
      near(jointPose(pivot,modeState('orbit',time)).quaternion.angleTo(jointPose(pivot).quaternion),0);
    }
    assert.ok(mount.interval[1]<=pivot.interval[0]);
    const arc=new Vector3(0,-1,0).applyQuaternion(jointPose(pivot,{transform:.22}).quaternion);
    near(arc.x,pivot.motion.side);
    near(Math.abs(jointPose(mount,{transform:.08}).position.x),weapon.kind==='rifle'?1.36:1.70);
    assert.ok(jointPose(mount,{transform:.08}).position.z>.8);
    assert.ok(jointPose(mount,{transform:1}).position.z<-.7);
    for(const transform of [.5,.7,.85,.9]){
      assert.ok(Math.abs(jointPose(mount,{transform}).position.x)>2.3,'clear the moving front axle');
    }
    near(jointPose(pivot,{transform:1}).quaternion.angleTo(jointPose(pivot).quaternion),Math.PI);
  }
});
test('weapon geometry and the amber blade material are embedded in the downloadable model',()=>{
  const buffer=readFileSync(new URL('../assets/optimus.glb',import.meta.url));
  const gltf=JSON.parse(buffer.subarray(20,20+buffer.readUInt32LE(12)).toString());
  const descendantMeshes=index=>{
    const node=gltf.nodes[index];
    return (node.mesh===undefined?0:1)+(node.children||[]).reduce((sum,child)=>sum+descendantMeshes(child),0);
  };
  for(const weapon of definition.weapons){
    const index=gltf.nodes.findIndex(node=>node.extras?.rigId===weapon.joint);
    assert.ok(index>=0);
    assert.ok(descendantMeshes(index)>=8,`${weapon.kind} must include real geometry`);
  }
  const amber=gltf.materials.find(material=>material.name==='Amber energon');
  assert.ok(amber);
  assert.ok(amber.pbrMetallicRoughness.baseColorFactor[0]>.9);
  assert.ok(amber.pbrMetallicRoughness.baseColorFactor[2]<.05);
});
