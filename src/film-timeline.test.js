import test from 'node:test';
import assert from 'node:assert/strict';
import { Quaternion,Vector3 } from 'three';
import { FILM,SHOTS,filmFrame } from './film-timeline.js';

test('preview has the requested resolution, cadence and four shot lengths',()=>{
  assert.deepEqual(FILM,{duration:80,fps:24,width:1920,height:1080});
  assert.deepEqual(SHOTS.map(shot=>shot.end-shot.start),[12,12,43,13]);
  assert.equal(FILM.duration*FILM.fps,1920);
});

test('train arrives, waits through the tour, then departs',()=>{
  assert.equal(filmFrame(0).trainX,-44);
  assert.equal(filmFrame(10).trainX,0);
  assert.equal(filmFrame(66).trainX,0);
  assert.equal(filmFrame(79).trainX,44);
  let last=-44;
  for(let t=0;t<=80;t+=.1){const x=filmFrame(t).trainX;assert.ok(x>=last-1e-9);last=x;}
});
test('doors only open after arrival and close before departure',()=>{
  assert.equal(filmFrame(10).doorAmount,0);
  assert.equal(filmFrame(12).doorAmount,1);
  assert.equal(filmFrame(69).doorAmount,0);
  for(let t=0;t<=80;t+=.1){
    const state=filmFrame(t);
    if(state.doorAmount>.001)assert.equal(state.trainX,0);
  }
});
test('rear doorway is open before the camera crosses its bulkhead',()=>{
  for(let t=42;t<=45;t+=1/FILM.fps){
    const state=filmFrame(t);
    if(state.position[0]>-9.3&&state.position[0]<-8.8){
      assert.ok(state.rearDoor>.99);
      assert.ok(Math.abs(state.position[2])<.36);
      assert.ok(state.position[1]<3.12);
    }
  }
});
test('both orbit shots make a complete 360-degree revolution',()=>{
  for(const [start,end,center] of [[12,24,[0,1.65,4.8]],[24,36,[0,1.7,0]]]){
    let total=0;
    let previous;
    for(let t=start;t<end;t+=.02){
      const p=filmFrame(t).position;
      const angle=Math.atan2(p[0]-center[0],p[2]-center[2]);
      if(previous!==undefined){
        let delta=angle-previous;
        while(delta<-Math.PI)delta+=Math.PI*2;
        while(delta>Math.PI)delta-=Math.PI*2;
        total+=delta;
      }
      previous=angle;
    }
    assert.ok(Math.abs(total-2*Math.PI)<.005);
  }
});
test('the orbit-to-cab-to-platform shot has continuous camera position and rotation',()=>{
  let previous=filmFrame(24);
  for(let t=24+1/FILM.fps;t<67;t+=1/FILM.fps){
    const state=filmFrame(t);
    const distance=new Vector3(...state.position).distanceTo(new Vector3(...previous.position));
    const angle=new Quaternion(...state.quaternion).angleTo(new Quaternion(...previous.quaternion));
    assert.ok(distance<.85,`Camera jump at ${t}: ${distance}`);
    assert.ok(angle<.15,`Camera rotation jump at ${t}: ${angle}`);
    previous=state;
  }
});
test('interior travel clears poles, cab partition and side-door jambs',()=>{
  for(let t=45;t<67;t+=1/FILM.fps){
    const state=filmFrame(t);
    const [x,y,z]=state.position;
    assert.ok(y>2.6);
    assert.ok(x<8.15);
    if(x>6.95&&x<7.3)assert.ok(Math.abs(z)<.37,`Cab jamb at ${t}`);
    if(z>1.30&&z<1.65){
      assert.ok(x>3.95&&x<5.1,`Side-door jamb at ${t}: ${x}`);
      assert.equal(state.doorAmount,1);
    }
    if(t<54)assert.ok(Math.abs(z)<.3);
  }
});
