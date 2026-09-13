import test from 'node:test';
import assert from 'node:assert/strict';
import { canOccupy, inDoorway, resolveMove, visitorArea } from './navigation.js';

test('platform and passenger aisle are walkable; tracks are not', () => {
  assert.ok(canOccupy({x:-12,z:3.75},false));
  assert.ok(canOccupy({x:1,z:0},false));
  assert.ok(!canOccupy({x:12,z:0},true));
  assert.ok(!canOccupy({x:0,z:8.6},true));
});
test('closed doors prevent boarding', () => {
  const end=resolveMove({x:-.50,z:2.5},{x:0,z:-2.5},false);
  assert.ok(end.z>=1.9);
});
test('open doors permit continuous boarding and alighting', () => {
  const end=resolveMove({x:-.50,z:2.5},{x:0,z:-2.5},true);
  assert.ok(Math.abs(end.z)<.01);
  assert.equal(visitorArea(end),'interior');
  const back=resolveMove(end,{x:0,z:2.5},true);
  assert.ok(back.z>2.4);
  assert.equal(visitorArea(back),'platform');
});
test('door closing guard detects visitors in the threshold', () => {
  assert.ok(inDoorway({x:-.5,z:1.55}));
  assert.ok(!inDoorway({x:2,z:1.55}));
});
test('columns and benches block the visitor', () => {
  assert.ok(!canOccupy({x:0,z:4.88},true));
  assert.ok(!canOccupy({x:3.25,z:4.9},true));
  assert.ok(!canOccupy({x:-9.75,z:5.60},true));
  const end=resolveMove({x:-1,z:4.88},{x:2,z:0},true);
  assert.ok(end.x<-.52);
});
test('passenger walls and poles cannot be crossed', () => {
  assert.ok(!canOccupy({x:1,z:1.4},true));
  assert.ok(!canOccupy({x:-.8,z:.57},true));
});
test('cab doorway works and desk / driver chair remain blocked', () => {
  assert.ok(canOccupy({x:7.14,z:.18},false));
  assert.ok(canOccupy({x:7.75,z:.18},false));
  assert.ok(!canOccupy({x:7.75,z:-.25},false));
  const end=resolveMove({x:7.75,z:.18},{x:2,z:0},false);
  assert.ok(end.x<=8.21);
});
test('stairs are a visual exit, not a walk-through to an unfinished area', () => {
  const end=resolveMove({x:-15,z:4},{x:-5,z:0},false);
  assert.ok(end.x>=-15.61);
});
