// A bounded, level visitor route, not a general rigid-body simulation.
export const DOOR_CENTERS = [-6.1, -.8, 4.5];
const COLUMNS = [-13, -6.5, 0, 6.5, 13];
const inRange = (value, min, max) => value >= min && value <= max;
const atDoor = (x) => DOOR_CENTERS.some(center => Math.abs(x-center) < .53);

export function inDoorway({ x, z }) {
  return atDoor(x) && inRange(z, 1.04, 1.90);
}

export function canOccupy({ x, z }, doorsOpen) {
  const platform = inRange(x, -15.6, 17.55) && inRange(z, 1.90, 7.63);
  const aisle = inRange(x, -8.45, 6.75) && Math.abs(z) <= .42;
  const vestibule = atDoor(x) && inRange(z, -.97, 1.20);
  const boarding = doorsOpen && atDoor(x) && inRange(z, .38, 2.10);
  const cabDoor = inRange(x, 6.70, 7.40) && Math.abs(z) <= .29;
  const cab = inRange(x, 7.35, 8.21) && inRange(z, .10, .85);
  if (!(platform || aisle || vestibule || boarding || cabDoor || cab)) return false;
  if (COLUMNS.some(center => Math.abs(x-center) < .53 && Math.abs(z-4.88) < .53)) return false;
  if ([-9.75,3.25,10].some(center => Math.abs(x-center) < 1.54 && inRange(z,4.48,5.48))) return false;
  if ([-9.75,3.25].some(center => Math.abs(x-center) < 1.58 && inRange(z,5.32,5.91))) return false;
  if (Math.abs(x+2.20)<.44 && Math.abs(z-5.52)<.32) return false;
  if (DOOR_CENTERS.some(center => Math.hypot(x-center,z-.57)<.18 || Math.hypot(x-center,z+.57)<.18)) return false;
  return true;
}

export function resolveMove(position, delta, doorsOpen) {
  const next = { x: position.x, z: position.z };
  // Substep long moves so callers cannot jump across columns or a closed door.
  const steps = Math.max(1, Math.ceil(Math.hypot(delta.x,delta.z)/.06));
  for (let step=0; step<steps; step++) {
    const alongX = { x: next.x+delta.x/steps, z: next.z };
    if (canOccupy(alongX,doorsOpen)) next.x=alongX.x;
    const alongZ = { x: next.x, z: next.z+delta.z/steps };
    if (canOccupy(alongZ,doorsOpen)) next.z=alongZ.z;
  }
  return next;
}

export function visitorArea({ x, z }) {
  if (z >= 1.90) return 'platform';
  return x >= 7.35 ? 'cab' : 'interior';
}
