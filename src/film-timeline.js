import { Vector3, Quaternion, Matrix4, CatmullRomCurve3 } from 'three';

export const FILM = { duration:80, fps:24, width:1920, height:1080 };
export const SHOTS = [
  { start:0, end:12, name:'地铁进站', en:'01 / ARRIVAL' },
  { start:12, end:24, name:'中央站 · 360°', en:'02 / CENTRAL STATION' },
  { start:24, end:67, name:'列车与车内漫游', en:'03 / M01 EXPERIENCE' },
  { start:67, end:80, name:'地铁离站', en:'04 / DEPARTURE' },
];
const clamp = value => Math.min(1,Math.max(0,value));
const smooth = value => { const t=clamp(value); return t*t*(3-2*t); };
const progress = (time,start,end) => clamp((time-start)/(end-start));
const v = values => new Vector3(...values);
const look = (position,target) => new Quaternion().setFromRotationMatrix(
  new Matrix4().lookAt(v(position),v(target),new Vector3(0,1,0)),
);
const pose = (position,target,fov) => ({position,quaternion:look(position,target).toArray(),fov});
const orbitEnd=[-22,8,0];

function path(points,targets,fovs) {
  return {
    curve:new CatmullRomCurve3(points.map(v),false,'centripetal'),
    rotations:points.map((point,index)=>look(point,targets[index])),
    fovs,
  };
}
function samplePath(definition,fraction) {
  const t=clamp(fraction);
  const cursor=t*(definition.rotations.length-1);
  const index=Math.min(definition.rotations.length-2,Math.floor(cursor));
  const local=cursor-index;
  return {
    position:definition.curve.getPoint(t).toArray(),
    quaternion:(definition.globalRotation
      ? definition.rotations[0].clone().slerp(definition.rotations.at(-1),smooth(t))
      : definition.rotations[index].clone().slerp(definition.rotations[index+1],smooth(local))).toArray(),
    fov:definition.fovs[index]+(definition.fovs[index+1]-definition.fovs[index])*smooth(local),
  };
}
const approach=path(
  [orbitEnd,[-17,6.5,3.5],[-13,3.8,1.2],[-11.2,2.70,0]],
  [[0,1.7,0],[-8,2.5,0],[-8.7,2.65,0],[-6,2.45,0]],
  [42,48,58,70],
);
const enter=path(
  [[-11.2,2.7,0],[-9.3,2.7,0],[-8,2.7,0]],
  [[-6,2.45,0],[-4.3,2.45,0],[-3,2.45,0]],
  [70,70,70],
);
const cabEnter=path(
  [[6.5,2.7,0],[7.12,2.72,.04],[7.55,2.76,.18],[7.8,2.76,.23]],
  [[11.5,2.45,0],[8.85,2.30,0],[8.84,2.15,0],[8.84,2.10,0]],
  [70,70,70,70],
);
const cabHold=path(
  [[7.8,2.76,.23],[7.94,2.73,.31]],
  [[8.84,2.10,0],[8.84,2.12,.04]],
  [70,70],
);
const cabExit=path(
  [[7.94,2.73,.31],[7.55,2.74,.23],[7.12,2.73,.05],[6.3,2.72,.10]],
  [[8.84,2.12,.04],[7.55,2.55,2.0],[3.0,2.55,.0],[2.0,2.5,0]],
  [70,70,70,70],
);
const alight=path(
  [[6.3,2.72,.10],[4.85,2.72,.10],[4.85,2.8,2.20],[5.4,2.9,3.75]],
  [[2,2.5,0],[4.4,2.6,2.6],[6.8,2.6,.2],[8.0,2.1,0]],
  [70,70,66,58],
);
alight.globalRotation=true;

export function filmFrame(seconds) {
  const t=Math.max(0,Math.min(FILM.duration,seconds));
  const shot=SHOTS.find(item=>t<item.end)||SHOTS.at(-1);
  let camera;
  let phase;
  if (t<12) {
    camera=pose([12.4,2.9,3.75],[-6.2,2.25,0],58);
    phase='arrival';
  } else if (t<24) {
    const a=Math.PI/4+2*Math.PI*smooth(progress(t,12,24));
    camera=pose([Math.sin(a)*42,27,4.8+Math.cos(a)*42],[0,1.65,4.8],42);
    phase='station-orbit';
  } else if (t<36) {
    const a=-Math.PI/2+2*Math.PI*smooth(progress(t,24,36));
    camera=pose([Math.sin(a)*22,8,Math.cos(a)*22],[0,1.7,0],42);
    phase='train-orbit';
  } else if (t<42) {
    camera=samplePath(approach,smooth(progress(t,36,42)));
    phase='rear-approach';
  } else if (t<45) {
    camera=samplePath(enter,progress(t,42,45));
    phase='rear-entry';
  } else if (t<54) {
    const x=-8+14.5*progress(t,45,54);
    camera=pose([x,2.7,0],[x+5,2.45,0],70);
    phase='saloon';
  } else if (t<57) {
    camera=samplePath(cabEnter,smooth(progress(t,54,57)));
    phase='cab-entry';
  } else if (t<60) {
    camera=samplePath(cabHold,smooth(progress(t,57,60)));
    phase='cab';
  } else if (t<63) {
    camera=samplePath(cabExit,smooth(progress(t,60,63)));
    phase='cab-exit';
  } else if (t<67) {
    camera=samplePath(alight,smooth(progress(t,63,67)));
    phase='alight';
  } else {
    camera=pose([-11,3.2,3.9],[8,2.1,0],57);
    phase='departure';
  }
  const arrival=progress(t,.8,10);
  const departure=progress(t,70,79);
  const trainX=t<10 ? -44*(1-arrival)**2 : t>=67 ? 44*departure**2 : 0;
  const doorAmount=smooth(progress(t,10.3,11.5))*(1-smooth(progress(t,67.4,68.6)));
  const rearDoor=smooth(progress(t,40.6,41.9))*(1-smooth(progress(t,46,47)));
  let stationAlpha=1;
  if (t>=24 && t<38) stationAlpha=0;
  else if (t>=38 && t<40.5) stationAlpha=smooth(progress(t,38,40.5));
  const cover=t<12||t>=40.5;
  const caption=t>=36&&t<45 ? '从车尾登车' : t>=45&&t<54 ? '穿行乘客车厢' :
    t>=54&&t<60 ? '进入驾驶室' : t>=60&&t<67 ? '离开驾驶室' : shot.name;
  return {
    time:t,phase,shot:SHOTS.indexOf(shot)+1,caption,chapter:shot.en,...camera,
    trainX,doorAmount,rearDoor,stationAlpha,cover,
    fade:Math.max(1-smooth(progress(t,0,.8)),smooth(progress(t,78.8,80))),
  };
}
