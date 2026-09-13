import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Box3, Group, PerspectiveCamera, Quaternion, Euler, Vector3 } from 'three';
import { bindRig, jointPose, filmState, modeState, CHAPTERS, fitCamera } from './optimus-rig.js';

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
test('the chassis clears the floor while the toes fold',()=>{
  const chassis=definition.joints.find(joint=>joint.id==='chassis');
  assert.ok(jointPose(chassis,{transform:.18}).position.y>chassis.robot[1]+.29);
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
