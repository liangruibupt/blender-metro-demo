import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createReadStream, existsSync, readFileSync, statSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import configuration from '../vite.config.js';

const root=fileURLToPath(new URL('../',import.meta.url));
const requiredAssets=[
  'metro/assets/metro.glb',
  'metro/assets/station.glb',
  'optimus/assets/optimus.glb',
  'optimus/assets/optimus-rig.json',
  'metro/deliverables/metro-storyboard-preview.mp4',
  'optimus/deliverables/optimus-showcase.mp4',
  'metro/deliverables/station-platform.png',
  'optimus/deliverables/optimus-robot.png',
];

async function checksum(file) {
  const hash=createHash('sha256');
  for await(const chunk of createReadStream(file))hash.update(chunk);
  return hash.digest('hex');
}

export async function checkDeployment(directory=resolve(root,'dist'),{url}={}) {
  const dist=resolve(directory);
  const manifest=JSON.parse(readFileSync(resolve(dist,'.vite/manifest.json'),'utf8'));
  const pages=Object.values(configuration.build.rollupOptions.input);
  const files=new Set([...pages,'favicon.svg']);
  for(const entry of Object.values(manifest)){
    if(entry.file)files.add(entry.file);
    for(const file of [...(entry.css||[]),...(entry.assets||[])])files.add(file);
    for(const imported of [...(entry.imports||[]),...(entry.dynamicImports||[])]){
      assert.ok(manifest[imported],`Missing chunk manifest entry: ${imported}`);
    }
  }
  for(const file of files){
    const path=resolve(dist,file);
    assert.ok(path.startsWith(dist+sep),`Output escapes deployment directory: ${file}`);
    assert.ok(existsSync(path)&&statSync(path).isFile(),`Missing deployment file: ${file}`);
  }
  for(const source of requiredAssets){
    const entry=Object.values(manifest).find(item=>item.src?.split('?')[0]===source);
    assert.ok(entry,`Asset not emitted by Vite: ${source}`);
    assert.equal(await checksum(resolve(dist,entry.file)),await checksum(resolve(root,source)),
      `Asset content changed during build: ${source}`);
  }
  let hosted;
  if(url){
    const base=new URL(url);
    assert.ok(['http:','https:'].includes(base.protocol),'Expected an HTTP(S) deployment URL');
    assert.ok(!base.search&&!base.hash,'Use the deployment directory URL without query or fragment');
    if(!base.pathname.endsWith('/'))base.pathname+='/';
    for(const file of files){
      const response=await fetch(new URL(file,base),{method:'HEAD',signal:AbortSignal.timeout(10000)});
      assert.equal(response.status,200,`HTTP ${response.status}: ${file}`);
      if(!file.endsWith('.html')){
        assert.ok(!response.headers.get('content-type')?.includes('text/html'),`HTML fallback served as ${file}`);
      }
    }
    for(const source of requiredAssets.filter(file=>file.endsWith('.mp4'))){
      const entry=Object.values(manifest).find(item=>item.src?.split('?')[0]===source);
      const response=await fetch(new URL(entry.file,base),{
        headers:{Range:'bytes=0-31'},signal:AbortSignal.timeout(10000),
      });
      await response.body?.cancel();
      assert.equal(response.status,206,`Host must support video byte ranges: ${source}`);
      assert.match(response.headers.get('content-range')||'',/^bytes 0-31\/\d+$/);
      assert.ok(response.headers.get('content-type')?.includes('video/mp4'),`Incorrect video MIME type: ${source}`);
    }
    hosted={url:base.href,filesChecked:files.size,videoRanges:2};
  }
  return {result:'PASS',pages:pages.length,files:files.size,assetsVerified:requiredAssets.length,...(hosted?{hosted}:{})};
}

if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const {values,positionals}=parseArgs({options:{url:{type:'string'}},allowPositionals:true});
  console.log(JSON.stringify(await checkDeployment(positionals[0],values),null,2));
}
