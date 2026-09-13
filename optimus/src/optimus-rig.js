import { Euler, Matrix4, Quaternion, Vector3 } from 'three';

export const clamp = (value, low=0, high=1) => Math.max(low, Math.min(high, value));
export const smooth = value => { const t=clamp(value); return t*t*(3-2*t); };
export const ramp = (value, start, end) => smooth((value-start)/(end-start));
export const DURATION = { orbit:12, exploded:8, assembly:12, transform:14, film:80 };
export const CHAPTERS = [
  {start:0,end:12,label:'机器人 · 360°',type:'orbit'},
  {start:12,end:20,label:'机械总成拆解',type:'exploded'},
  {start:20,end:28,label:'爆炸图 · 360°',type:'exploded'},
  {start:28,end:40,label:'分层组装',type:'assembly'},
  {start:40,end:44,label:'机器人形态',type:'orbit'},
  {start:44,end:58,label:'机器人 → 卡车',type:'transform'},
  {start:58,end:66,label:'卡车 · 360°',type:'orbit'},
  {start:66,end:80,label:'卡车 → 机器人',type:'transform'},
];

export function fitCamera(frame, bounds, aspect, fov=40) {
  const target=bounds.getCenter(new Vector3());
  const direction=new Vector3(...frame.camera).sub(new Vector3(...frame.target));
  const basis=new Matrix4().lookAt(direction,new Vector3(),new Vector3(0,1,0));
  const right=new Vector3().setFromMatrixColumn(basis,0);
  const up=new Vector3().setFromMatrixColumn(basis,1);
  const back=new Vector3().setFromMatrixColumn(basis,2);
  const tangent=Math.tan(fov*Math.PI/360);
  let distance=direction.length();
  // Fit every corner, accounting for depth, rather than guessing from robot height.
  for(const x of [bounds.min.x,bounds.max.x]){
    for(const y of [bounds.min.y,bounds.max.y]){
      for(const z of [bounds.min.z,bounds.max.z]){
        const offset=new Vector3(x,y,z).sub(target);
        const depth=offset.dot(back);
        distance=Math.max(distance,1.12*Math.abs(offset.dot(right))/(tangent*aspect)+depth,
          1.12*Math.abs(offset.dot(up))/tangent+depth);
      }
    }
  }
  return {position:direction.normalize().multiplyScalar(distance).add(target),target};
}

export function jointPose(joint, {transform=0, explosion=0, assembly=null}={}) {
  const phase=ramp(clamp(transform),...joint.interval);
  const position=new Vector3(...joint.robot).lerp(new Vector3(...joint.truck),phase);
  const quaternion=new Quaternion().setFromEuler(new Euler(...joint.angles));
  quaternion.slerp(new Quaternion().setFromEuler(new Euler(...joint.truckAngles)),phase);
  if(joint.motion?.type==='roof'){
    position.x+=joint.motion.side*.84*ramp(transform,.02,.12)*(1-ramp(transform,.38,.53));
  }
  if(joint.motion?.type==='shoulder'){
    position.x+=joint.motion.side*.48*ramp(transform,.12,.25)*(1-ramp(transform,.50,.8));
  }
  if(joint.motion?.type==='lift'){
    position.y+=.30*ramp(transform,.02,.10)*(1-ramp(transform,.35,.50));
  }
  const amount=assembly===null?clamp(explosion):
    1-ramp(clamp(assembly),joint.order*.075,joint.order*.075+.36);
  position.addScaledVector(new Vector3(...joint.explode),amount);
  return {position,quaternion};
}

export function filmState(seconds) {
  const time=clamp(seconds,0,80);
  const chapter=CHAPTERS.find(item=>time<item.end)||CHAPTERS.at(-1);
  const transform=ramp(time,44,58)*(1-ramp(time,66,79));
  const assembly=time>=28&&time<40?(time-28)/12:null;
  const explosion=time>=12&&time<28?ramp(time,12,20):0;
  const extent=assembly===null?explosion:1-ramp(assembly,.58,1);
  const angle=.6+2*Math.PI*ramp(time,0,12)+.35*ramp(time,12,20)+
    2*Math.PI*ramp(time,20,28)+.45*ramp(time,28,40)+.25*ramp(time,40,44)+
    1.65*ramp(time,44,58)+2*Math.PI*ramp(time,58,66)+1.3*ramp(time,66,80);
  const radius=15+7*extent-5*transform;
  return {
    time,transform,explosion,assembly,chapter:chapter.label,
    camera:[Math.sin(angle)*radius,6.8+3*extent-2.5*transform,Math.cos(angle)*radius],
    target:[0,4+2*extent-2.5*transform,0],
  };
}

export function modeState(mode, seconds, truck=false) {
  const time=clamp(seconds,0,DURATION[mode]);
  if(mode==='film')return filmState(time);
  const transform=mode==='transform'?smooth(time/14):(mode==='orbit'&&truck?1:0);
  const explosion=mode==='exploded'?smooth(time/8):0;
  const assembly=mode==='assembly'?time/12:null;
  const extent=assembly===null?explosion:1-ramp(assembly,.58,1);
  const angle=.6+(mode==='orbit'?2*Math.PI*time/12:
    mode==='assembly'?.55*smooth(time/12):mode==='transform'?1.65*smooth(time/14):.3*explosion);
  const radius=15+7*extent-5*transform;
  return {time,transform,explosion,assembly,
    chapter:{orbit:'360° 环绕',exploded:'机械总成拆解',assembly:'分层组装',transform:'机器人 → 卡车'}[mode],
    camera:[Math.sin(angle)*radius,6.8+3*extent-2.5*transform,Math.cos(angle)*radius],
    target:[0,4+2*extent-2.5*transform,0]};
}

export function bindRig(scene, definition) {
  const bindings=new Map();
  scene.traverse(object=>{if(object.userData.rigId)bindings.set(object.userData.rigId,object);});
  for(const joint of definition.joints){
    if(!bindings.has(joint.id))throw new Error(`缺少关节：${joint.id}`);
  }
  return {
    bindings,
    apply(state) {
      for(const joint of definition.joints){
        const object=bindings.get(joint.id);
        const pose=jointPose(joint,state);
        object.position.copy(pose.position);
        object.quaternion.copy(pose.quaternion);
      }
      scene.updateMatrixWorld(true);
    },
  };
}
