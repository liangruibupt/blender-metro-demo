import test from 'node:test';
import assert from 'node:assert/strict';
import { ORBIT_LIMITS, inspectionView, inspectionLayers } from './inspection.js';

test('orbit permits upper and lower hemispheres without pole singularities', () => {
  assert.ok(ORBIT_LIMITS.minPolarAngle>0);
  assert.ok(ORBIT_LIMITS.maxPolarAngle>Math.PI/2);
  assert.ok(ORBIT_LIMITS.maxPolarAngle<Math.PI);
});
for (const scope of ['train','station']) {
  test(`${scope} gets distinct above and below camera presets`, () => {
    for (const [width,height] of [[1440,1000],[390,844],[360,740]]) {
      const above=inspectionView(scope,false,width,height);
      const below=inspectionView(scope,true,width,height);
      assert.ok(above.position[1]>above.target[1]);
      assert.ok(below.position[1]<0);
      assert.deepEqual(above.target,below.target);
      const distance=Math.hypot(...below.position.map((v,i)=>v-below.target[i]));
      assert.ok(below.maxDistance>distance);
      assert.ok(below.position.every(Number.isFinite));
    }
  });
}
test('train bottom view hides station, ground and tracks, not train geometry', () => {
  assert.deepEqual(inspectionLayers('exterior','train',-8),{
    below:true,ground:false,station:false,stationCover:false,
    foundation:false,trainTrack:false,undersideLight:true,
  });
});
test('station bottom view keeps platform and rails, hides presentation slab', () => {
  const state=inspectionLayers('exterior','station',-20);
  assert.ok(state.station && state.trainTrack);
  assert.ok(!state.ground && !state.foundation && !state.stationCover);
});
test('upper orbit restores environmental occluders', () => {
  const state=inspectionLayers('exterior','station',12);
  assert.ok(state.ground && state.foundation && state.trainTrack);
  assert.ok(!state.below && !state.undersideLight);
});
test('first-person views restore the station regardless of inspection scope', () => {
  for (const mode of ['platform','interior','cab']) {
    const state=inspectionLayers(mode,'train',-1);
    assert.ok(state.station && state.stationCover && state.foundation && state.ground);
    assert.ok(!state.below);
  }
});
