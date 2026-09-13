export const ORBIT_LIMITS = { minPolarAngle: .035, maxPolarAngle: Math.PI-.035 };

export function inspectionMeshRole(name, zone) {
  if (name === 'Station_foundation') return 'foundation';
  if (zone === '04_Roof') return 'roof';
  if (zone === '10_Station_Cover') return 'stationCover';
  if (zone === '07_Track') return name.startsWith('Trackbed') ? 'trainBed' : 'trainTrack';
  if (['Platform_structure','Platform_grout_bed','Platform_floor_tile','Station_ballast']
    .some(prefix => name.startsWith(prefix))) return 'stationDeck';
  return null;
}

export function inspectionView(scope, bottom, width, height) {
  const train = scope === 'train';
  const target = train ? [0,1.25,0] : [0,1.65,4.8];
  const above = train ? [22,11.5,24] : [31,29,39];
  const below = train ? [15,-9,17] : [31,-24,39];
  const fov = width < 600 ? 46 : 38;
  const position = bottom ? below : above;
  const direction = position.map((value,index) => value-target[index]);
  const originalDistance = Math.hypot(...direction);
  const horizontalHalfFov = Math.atan(Math.tan(fov*Math.PI/360)*width/height);
  const fitDistance = (train ? 11.2 : 25) / Math.sin(horizontalHalfFov);
  const distance = Math.max(originalDistance, fitDistance);
  return {
    position: direction.map((value,index) => target[index]+value/originalDistance*distance),
    target,
    fov,
    maxDistance: Math.max(100,distance*1.5),
  };
}

export function inspectionLayers(mode, scope, cameraHeight) {
  const orbit = mode === 'exterior';
  const below = orbit && cameraHeight < .2;
  const fullStation = !orbit || scope === 'station';
  return {
    below,
    ground: !below,
    station: fullStation,
    stationCover: !orbit,
    foundation: fullStation && !below,
    trainTrack: fullStation || !below,
    trainBed: !below,
    stationDeck: fullStation && !below,
    stationXray: fullStation && below,
    undersideLight: below,
  };
}
