import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import configuration from '../vite.config.js';

const root=fileURLToPath(new URL('../',import.meta.url));
const inputs=Object.values(configuration.build.rollupOptions.input);

test('each task owns its source, models, scripts, deliverables and documentation',()=>{
  for(const task of ['metro','optimus']){
    for(const folder of ['src','assets','scripts','deliverables']){
      assert.ok(statSync(resolve(root,task,folder)).isDirectory(),`${task}/${folder}`);
    }
    for(const file of ['index.html','watch.html','README.md','QA.md']){
      assert.ok(statSync(resolve(root,task,file)).isFile(),`${task}/${file}`);
    }
  }
});
test('all five canonical task pages are deployment inputs',()=>{
  for(const page of ['metro/index.html','metro/film.html','metro/watch.html','optimus/index.html','optimus/watch.html']){
    assert.ok(inputs.includes(page),page);
  }
});
test('legacy page URLs stay in the deployment and every input exists',()=>{
  for(const page of ['index.html','film.html','watch.html','optimus.html','optimus-watch.html']){
    assert.ok(inputs.includes(page),page);
  }
  for(const page of inputs)assert.ok(statSync(resolve(root,page)).isFile(),page);
  assert.equal(inputs.length,new Set(inputs).size);
});
test('no task source or binary assets remain in the former shared directories',()=>{
  for(const folder of ['src','deliverables','public/assets']){
    assert.equal(existsSync(resolve(root,folder)),false,folder);
  }
});
test('build uses relative URLs and emits a machine-verifiable deployment manifest',()=>{
  assert.equal(configuration.base,'./');
  assert.equal(configuration.appType,'mpa');
  assert.equal(configuration.build.manifest,true);
});
