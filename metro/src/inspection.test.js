import test from 'node:test';
import assert from 'node:assert/strict';
import { ORBIT_LIMITS, inspectionView, inspectionLayers, inspectionMeshRole } from './inspection.js';

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
    trainBed:false,stationDeck:false,stationXray:false,
  });
});
test('station bottom view reveals rails and train through the deck and rail beds', () => {
  const state=inspectionLayers('exterior','station',-20);
  assert.ok(state.station && state.trainTrack);
  assert.ok(!state.ground && !state.foundation && !state.stationCover);
  assert.ok(!state.stationDeck && !state.trainBed && state.stationXray);
});
test('upper orbit restores environmental occluders', () => {
  const state=inspectionLayers('exterior','station',12);
  assert.ok(state.ground && state.foundation && state.trainTrack && state.stationDeck && state.trainBed);
  assert.ok(!state.stationXray);
  assert.ok(!state.below && !state.undersideLight);
});
test('first-person views restore the station regardless of inspection scope', () => {
  for (const mode of ['platform','interior','cab']) {
    const state=inspectionLayers(mode,'train',-1);
    assert.ok(state.station && state.stationCover && state.foundation && state.ground);
    assert.ok(state.stationDeck && state.trainBed && !state.stationXray);
    assert.ok(!state.below);
  }
});
test('all horizontal opaque deck layers are separated for x-ray rendering', () => {
  for (const name of ['Platform_structure','Platform_grout_bed','Platform_floor_tile',
    'Platform_floor_tile.042','Platform_floor_tile_042','Station_ballast','Station_ballast_001']) {
    assert.equal(inspectionMeshRole(name,'09_Station'),'stationDeck');
  }
  assert.equal(inspectionMeshRole('Trackbed','07_Track'),'trainBed');
});
test('x-ray grouping preserves actual rails, sleepers and train running gear', () => {
  for (const name of ['Rail_head','Rail_web','Sleeper']) {
    assert.equal(inspectionMeshRole(name,'07_Track'),'trainTrack');
  }
  for (const name of ['Station_rail_head','Station_rail_web','Station_sleeper','Station_column']) {
    assert.equal(inspectionMeshRole(name,'09_Station'),null);
  }
  assert.equal(inspectionMeshRole('Bogie_frame','05_Undercarriage'),null);
  assert.equal(inspectionMeshRole('Wheel_tread','05_Undercarriage'),null);
});
test('separate train overview does not leak station floor or x-ray geometry', () => {
  const state=inspectionLayers('exterior','train',12);
  assert.ok(state.trainTrack && state.trainBed);
  assert.ok(!state.stationDeck && !state.stationXray);
});
