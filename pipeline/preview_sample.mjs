import {spawn} from 'node:child_process';
import {mkdtemp, readFile, writeFile, mkdir, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const root=resolve(import.meta.dirname,'..');
const editionArgument=process.argv.indexOf('--edition');
const edition=editionArgument<0?'2026-11-19-sample-02':process.argv[editionArgument+1];
if(!/^\d{4}-\d{2}-\d{2}(?:-sample-0[23])?$/.test(edition))throw new Error('Unknown edition');
const provenance=JSON.parse(await readFile(join(root,'data/editions',edition,'provenance.json'),'utf8'));
const expanded=provenance.pages===6;
const expectedSources=provenance.source_records_adopted??provenance.adopted_source_records;
const expectedCandidates=provenance.rss_candidates??provenance.rss_candidate_count;
const tabSelector=expanded?'[data-spread]':'[data-page]';
const pageSelector=expanded?'.spread:not([hidden]) .page':'.page:not([hidden])';
const output=join(root,'data/editions',edition,'preview');
await mkdir(output,{recursive:true});
const profile=await mkdtemp(join(tmpdir(),'cyber-daily-preview-'));
const chrome=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',[
  '--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'
],{stdio:'ignore'});
let websocket;
const failures=[];
const reports=[];
try{
  let port;
  for(let attempt=0;attempt<100;attempt++){
    try{port=(await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch{}
    await new Promise(resolveWait=>setTimeout(resolveWait,100));
  }
  if(!port)throw new Error('Chrome did not create a debugging port');
  const target=await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
  websocket=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolveOpen,rejectOpen)=>{websocket.addEventListener('open',resolveOpen,{once:true});websocket.addEventListener('error',rejectOpen,{once:true})});
  const pending=new Map();
  let sequence=0;
  websocket.addEventListener('message',event=>{
    const message=JSON.parse(event.data);
    const request=pending.get(message.id);
    if(request){pending.delete(message.id);clearTimeout(request.timer);message.error?request.reject(new Error(JSON.stringify(message.error))):request.resolve(message.result)}
    if(message.method==='Runtime.exceptionThrown')failures.push(message.params.exceptionDetails.text);
  });
  const call=(method,params={})=>new Promise((resolveCall,rejectCall)=>{
    const identifier=++sequence;
    const timer=setTimeout(()=>{pending.delete(identifier);rejectCall(new Error(`Timed out: ${method}`))},15000);
    pending.set(identifier,{resolve:resolveCall,reject:rejectCall,timer});
    websocket.send(JSON.stringify({id:identifier,method,params}));
  });
  const evaluate=async expression=>{
    const result=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if(result.exceptionDetails)throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await call('Page.enable');
  await call('Runtime.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1050,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:pathToFileURL(join(root,'cyber-daily-'+edition+'.html')).href});
  for(let attempt=0;attempt<100;attempt++){
    if(await evaluate("document.readyState==='complete' && !!document.querySelector('#audit-open')"))break;
    await new Promise(resolveWait=>setTimeout(resolveWait,100));
  }
  await evaluate('document.fonts.ready.then(()=>true)');
  if(provenance.weather){
    const weather=await evaluate("(()=>{const nodes=document.querySelectorAll('.weather-strip');const card=nodes[0];return {count:nodes.length,onFront:!!card?.closest('#page-1'),date:card?.dataset.date,text:card?.textContent}})()");
    if(weather.count!==1||!weather.onFront||weather.date!==edition||!weather.text.includes(provenance.weather.current.temperature.toFixed(1))||!weather.text.includes('汾湖'))failures.push('Front-page weather does not match collected data');
  }
  const inspect=async label=>{
    const report=await evaluate(`(()=>{
      const pages=Array.from(document.querySelectorAll('${pageSelector}'));
      const displayedPages=Array.from(document.querySelectorAll('.page')).filter(page=>page.getClientRects().length).map(page=>page.id);
      const escaped=pages.flatMap(page=>{
        const pageBox=page.getBoundingClientRect();
        return Array.from(page.querySelectorAll('article,table,h1,p,svg,img,.weather-strip,.weather-strip>*')).filter(element=>{
          const box=element.getBoundingClientRect();
          return box.right>pageBox.right+1 || box.left<pageBox.left-1;
        }).map(element=>page.id+':'+element.tagName+':'+element.textContent.slice(0,30));
      });
      return {pages:pages.map(page=>page.id),displayedPages,width:innerWidth,documentWidth:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,escaped,storyCount:pages.reduce((count,page)=>count+page.querySelectorAll('[data-story]').length,0)};
    })()`);
    report.label=label;
    reports.push(report);
    if(report.documentWidth>report.width+1 || report.escaped.length || JSON.stringify(report.pages)!==JSON.stringify(report.displayedPages))failures.push(report);
    const screenshot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:report.width,height:report.height,scale:1}});
    await writeFile(join(output,label+'.png'),Buffer.from(screenshot.data,'base64'));
  };
  for(let pageIndex=0;pageIndex<4;pageIndex++){
    await evaluate(`document.querySelectorAll('${tabSelector}')[${pageIndex}].click()`);
    await inspect('desktop-'+(pageIndex+1));
  }
  await evaluate("document.querySelector('#audit-open').click()");
  const audit=await evaluate("({open:document.querySelector('#audit').open,sources:document.querySelectorAll('#audit details').length,text:document.querySelector('#audit').textContent})");
  if(!audit.open || audit.sources!==expectedSources || !audit.text.includes(String(expectedCandidates)))failures.push('Audit dialog does not match provenance');
  await evaluate("document.querySelector('#audit-close').click();document.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}))");
  if(await evaluate(`document.querySelector('${pageSelector}').id`)!==(expanded?'page-5':'page-3'))failures.push('Keyboard paging failed');
  if(expanded){
    if(await evaluate("document.querySelectorAll('.page').length")!==6)failures.push('Six physical pages were not rendered');
    await evaluate("document.querySelectorAll('[data-spread]')[0].click()");
    const paired=await evaluate("(()=>{const pages=document.querySelectorAll('#spread-0 .page');const a=pages[0].getBoundingClientRect(),b=pages[1].getBoundingClientRect();return b.left>a.right&&Math.abs(a.top-b.top)<1})()");
    if(!paired)failures.push('Desktop politics pages are not side by side');
    await evaluate("document.querySelector('#layout-toggle').click()");
    const vertical=await evaluate("(()=>{const pages=document.querySelectorAll('#spread-0 .page');const a=pages[0].getBoundingClientRect(),b=pages[1].getBoundingClientRect();return b.top>a.bottom&&Math.abs(a.left-b.left)<1})()");
    if(!vertical)failures.push('Vertical reading toggle failed');
    await evaluate("document.querySelector('#layout-toggle').click();document.querySelectorAll('[data-spread]')[3].click()");
    const image=await evaluate("({loaded:document.querySelector('#art-open').complete,width:document.querySelector('#art-open').naturalWidth,height:document.querySelector('#art-open').naturalHeight})");
    if(!image.loaded||image.width<500||image.height<500)failures.push('Original painting did not load');
    await evaluate("document.querySelector('#art-open').click()");
    if(!await evaluate("document.querySelector('#art-view').open"))failures.push('Painting enlargement failed');
    await evaluate("document.querySelector('#art-close').click();document.querySelector('#art-open').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))");
    if(!await evaluate("document.querySelector('#art-view').open"))failures.push('Painting keyboard enlargement failed');
    await evaluate("document.querySelector('#art-close').click()");
  }
  for(const width of [820,390]){
    await call('Emulation.setDeviceMetricsOverride',{width,height:844,deviceScaleFactor:1,mobile:width<650});
    for(let pageIndex=0;pageIndex<4;pageIndex++){
      await evaluate(`document.querySelectorAll('${tabSelector}')[${pageIndex}].click()`);
      await inspect((width<650?'mobile':'tablet')+'-'+(pageIndex+1));
    }
  }
  const result={edition,reports,failures,checks:['4 sections rendered at 1440/820/390 px','source dialog opens and closes',`${expectedSources} source records in dialog`,'keyboard paging','no horizontal page overflow','no uncaught JavaScript exceptions',...(expanded?['6 physical pages','desktop side-by-side pages','vertical reading toggle','original painting image loads','painting enlargement by click and keyboard']:[]),...(provenance.weather?['weather appears once on the front page','weather date, location and current temperature match the API data']:[])]};
  await writeFile(join(output,'qa.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify({screenshots:reports.length,failures,reports},null,2));
  if(failures.length)process.exitCode=1;
}finally{
  websocket?.close();
  const stopped=new Promise(resolveStop=>chrome.once('exit',resolveStop));
  chrome.kill('SIGTERM');
  await Promise.race([stopped,new Promise(resolveWait=>setTimeout(resolveWait,3000))]);
  await rm(profile,{recursive:true,force:true,maxRetries:3,retryDelay:200});
}
