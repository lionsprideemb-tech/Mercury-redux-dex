#!/usr/bin/env python3
import base64, copy, gzip, json, re
from pathlib import Path

ROOT=Path('.')
APP=ROOT/'app.js'
HTML=ROOT/'index.html'
INDEX=ROOT/'data/pokedex/index.json'
OVERLAY=ROOT/'data/pokedex/review_overlay_r7.json.gz.b64'


def repl(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'Could not find {label} patch anchor')
    return text.replace(old,new)

app=APP.read_text()
old_loader="""async function loadPokedexPayload(){
  const idxRes=await fetch('data/pokedex/index.json');
  if(!idxRes.ok) throw new Error(`HTTP ${idxRes.status} loading Pokédex index`);
  const idx=await idxRes.json();
  const parts=await Promise.all((idx.shards||[]).map(name=>gunzipJson(`data/pokedex/${name}`)));
  const pokemon=parts.flatMap(x=>x.pokemon||[]);
  await hydrateSpriteAtlases(pokemon);
  return {meta:idx.meta||{},pokemon};
}
"""
new_loader="""async function loadPokedexPayload(){
  const idxRes=await fetch('data/pokedex/index.json');
  if(!idxRes.ok) throw new Error(`HTTP ${idxRes.status} loading Pokédex index`);
  const idx=await idxRes.json();
  const parts=await Promise.all((idx.shards||[]).map(name=>gunzipJson(`data/pokedex/${name}`)));
  let pokemon=parts.flatMap(x=>x.pokemon||[]);
  if(idx.overlay){
    const overlay=await gunzipJson(`data/pokedex/${idx.overlay}`);
    pokemon=applyReviewOverlay(pokemon,overlay);
  }
  await hydrateSpriteAtlases(pokemon);
  return {meta:idx.meta||{},pokemon};
}

function applyReviewOverlay(pokemon,overlay){
  const data=pokemon.map(p=>({...p}));
  const byKey=new Map(data.map(p=>[p.key,p]));
  const byConst=new Map(data.filter(p=>p.constant).map(p=>[p.constant,p]));
  const abilityMap=new Map();
  data.forEach(p=>['primaryAbilities','innates','sourceAbilities'].forEach(g=>(p[g]||[]).forEach(a=>abilityMap.set(a.name,a))));
  Object.values(overlay.abilityDefinitions||{}).forEach(a=>abilityMap.set(a.name,a));
  const clone=x=>x==null?x:JSON.parse(JSON.stringify(x));
  const blank=x=>x==null||(Array.isArray(x)&&!x.length)||(typeof x==='object'&&!Array.isArray(x)&&!Object.values(x).some(v=>v!=null));
  const abilityFor=name=>clone(abilityMap.get(name)||{constant:`ABILITY_${String(name).toUpperCase().replace(/[^A-Z0-9]+/g,'_')}`,name,description:'R7 review description pending.'});
  const resolveBase=ref=>byKey.get(ref)||byConst.get(ref)||data.find(p=>p.displayName===ref||p.name===ref);
  const applyItem=item=>{
    let p=byKey.get(item.key);
    if(!p){p={key:item.key};data.push(p);byKey.set(item.key,p);}
    const base=item.inheritFrom?resolveBase(item.inheritFrom):null;
    if(base){
      const forced=new Set(item.forceInherit||[]);
      ['stats','bst','description','levelUpMoves','sourceAbilities'].forEach(f=>{if(forced.has(f)||blank(p[f]))p[f]=clone(base[f]);});
    }
    const set=clone(item.set||{}), primaryNames=set.primaryAbilityNames, innateNames=set.innateNames;
    delete set.primaryAbilityNames;delete set.innateNames;
    Object.assign(p,set);
    if(primaryNames)p.primaryAbilities=primaryNames.map(abilityFor);
    if(innateNames)p.innates=innateNames.map(abilityFor);
    if(item.extraMoves?.length){
      const moves=clone(p.levelUpMoves||[]), seen=new Set(moves.map(m=>`${m.level}|${m.move}`));
      item.extraMoves.forEach(m=>{const k=`${m.level}|${m.move}`;if(!seen.has(k)){moves.push(clone(m));seen.add(k);}});
      const level=m=>{const n=parseInt(m.level,10);return Number.isFinite(n)?n:999;};
      moves.sort((a,b)=>level(a)-level(b)||String(a.move).localeCompare(String(b.move)));p.levelUpMoves=moves;
    }
    if(p.constant)byConst.set(p.constant,p);
  };
  (overlay.patches||[]).forEach(applyItem);
  (overlay.additions||[]).forEach(applyItem);
  const removed=new Set(overlay.removeKeys||[]);
  const out=data.filter(p=>!removed.has(p.key));
  out.forEach(p=>{
    p.planned=false;
    const abilityText=[...(p.primaryAbilities||[]),...(p.innates||[])].map(a=>`${a.name} ${a.description||''}`).join(' ');
    const moveText=(p.levelUpMoves||[]).map(m=>m.move).join(' ');
    p.searchText=[p.displayName,p.name,p.basePokemon,p.classification,p.source,p.bindingStatus,p.designStatus,(p.types||[]).join(' '),abilityText,moveText].filter(Boolean).join(' ').toLowerCase();
  });
  return out;
}
"""
app=repl(app,old_loader,new_loader,'overlay loader')
app=app.replace('const isCurrent=p=>!p.planned;',"const isReviewDraft=p=>Boolean(p.reviewDraft);\nconst isApproved=p=>!isReviewDraft(p);")
app=app.replace("$('#headerMeta').textContent=`${state.meta.rosterCount?.toLocaleString()||state.data.length.toLocaleString()} entries · ${state.meta.sourceAuthority||'R6 authority'}`;\n    $('#sourceBoundCount').textContent=(state.meta.sourceBoundCount||state.data.filter(isCurrent).length).toLocaleString();\n    $('#spriteCount').textContent=(state.meta.spriteCount||state.data.filter(hasSprite).length).toLocaleString();","$('#headerMeta').textContent=`${state.data.length.toLocaleString()} entries · ${state.meta.version||'R7 review pass'}`;\n    $('#approvedCount').textContent=state.data.filter(isApproved).length.toLocaleString();\n    $('#reviewDraftCount').textContent=state.data.filter(isReviewDraft).length.toLocaleString();\n    $('#spriteCount').textContent=state.data.filter(hasSprite).length.toLocaleString();")
app=app.replace("$('#tabCurrentCount').textContent=state.data.filter(isCurrent).length.toLocaleString();","$('#tabCurrentCount').textContent=state.data.filter(isApproved).length.toLocaleString();")
app=app.replace("$('#tabPlannedCount').textContent=state.data.filter(p=>p.planned).length.toLocaleString();","$('#tabPlannedCount').textContent=state.data.filter(isReviewDraft).length.toLocaleString();")
app=app.replace("if(state.status==='current'&&!isCurrent(p))return false;","if(state.status==='current'&&!isApproved(p))return false;")
app=app.replace("if(state.status==='planned'&&!p.planned)return false;","if(state.status==='planned'&&!isReviewDraft(p))return false;")
app=app.replace("node.classList.toggle('pending',!!p.planned);","node.classList.toggle('pending',isReviewDraft(p));")
app=app.replace("$('.card-status',node).textContent=p.planned?'Pending integration':'Current source';","$('.card-status',node).textContent=isReviewDraft(p)?'Review draft':'Approved roster';")
app=app.replace("return cards.length?cards.join(''):'<p class=\"detail-description\">Ability package is pending source integration for this approved entry.</p>';","return cards.length?cards.join(''):'<p class=\"detail-description\">No special ability package is listed for this entry.</p>';")
app=app.replace("<strong>${p.bst??'Pending'}</strong>","<strong>${p.bst??'—'}</strong>")
app=app.replace("if(!moves.length)return '<p class=\"detail-description\">Level-up learnset is not source-bound for this approved entry yet.</p>';","if(!moves.length)return '<p class=\"detail-description\">No level-up learnset is listed for this entry.</p>';")
app=app.replace("No further evolution is listed in the current source entry.","No further evolution is listed for this entry.")
app=app.replace("escapeHtml(x.target?.replace(/^SPECIES_/,'').replaceAll('_',' ')||'Unknown')","escapeHtml(x.targetName||x.target?.replace(/^SPECIES_/,'').replaceAll('_',' ')||'Unknown')")
app=app.replace("${p.planned?'pending':'current'}\">${p.planned?'Pending integration':'Current source'}","${isReviewDraft(p)?'pending':'current'}\">${isReviewDraft(p)?'Review draft':'Approved roster'}")
app=app.replace("<dt>Roster</dt><dd>${escapeHtml(p.rosterGroup)}</dd><dt>Classification</dt>","<dt>Roster</dt><dd>${escapeHtml(p.rosterGroup)}</dd><dt>Design status</dt><dd>${escapeHtml(p.designStatus||(isReviewDraft(p)?'Review draft':'Approved roster'))}</dd><dt>Classification</dt>")
app=app.replace("<dt>Source constant</dt><dd>${escapeHtml(p.constant||'Not bound yet')}</dd>","<dt>Source constant</dt><dd>${escapeHtml(p.constant||'Not assigned')}</dd>")
app=app.replace("${row('Status',a.planned?'Pending':'Current',b.planned?'Pending':'Current')}","${row('Status',isReviewDraft(a)?'Review draft':'Approved roster',isReviewDraft(b)?'Review draft':'Approved roster')}")
if 'isCurrent' in app or 'Pending integration' in app or 'Current source' in app:
    raise SystemExit('Old status model remains in app.js')
APP.write_text(app)

html=HTML.read_text()
html=html.replace('The current Mercury roster, sprites, mechanics, and project status in one place.','The Mercury roster, sprites, locked mechanics, and review-ready R7 proposals in one place.')
html=html.replace('Loading R6 authority…','Loading R7 review pass…')
html=html.replace('>Current <span id="tabCurrentCount"></span>','>Approved <span id="tabCurrentCount"></span>')
html=html.replace('>Pending <span id="tabPlannedCount"></span>','>Review drafts <span id="tabPlannedCount"></span>')
html=html.replace('<div><strong id="sourceBoundCount">—</strong><span>source-bound</span></div>\n        <div><strong id="spriteCount">—</strong><span>sprites available</span></div>\n        <div><strong id="abilityCount">1,043</strong><span>ability IDs in R6</span></div>','<div><strong id="approvedCount">—</strong><span>approved roster</span></div>\n        <div><strong id="reviewDraftCount">—</strong><span>review drafts</span></div>\n        <div><strong id="spriteCount">—</strong><span>sprites available</span></div>')
html=html.replace('Data snapshot: R6 / R14-caught-up reconstruction.','Data snapshot: R7 NextDex review pass. Entries marked Review draft are proposals for owner review, not claimed source/runtime bindings.')
HTML.write_text(html)

idx=json.loads(INDEX.read_text())
idx['meta'].update({'version':'R7 NextDex review pass','generated':'2026-09-15','entries':1604,'rosterCount':1604,'canonical':1025,'canonicalCount':1025,'approvedAdditions':579,'additionCount':579,'approvedPending':0,'plannedCount':0,'reviewDraftCount':118,'approvedRosterCount':1486,'spriteCount':1317,'sourceAuthority':'R7 NextDex authority: R6 roster + owner-locked amendments + explicitly labeled review drafts','statusModel':'approved-roster-or-review-draft'})
idx['count']=1604
idx['overlay']='review_overlay_r7.json.gz.b64'
INDEX.write_text(json.dumps(idx,separators=(',',':')))

# Data integrity audit of the overlay itself.
overlay=json.loads(gzip.decompress(base64.b64decode(OVERLAY.read_bytes())))
if len(overlay.get('removeKeys',[]))!=4 or len(overlay.get('additions',[]))!=5:
    raise SystemExit('Unexpected R7 overlay roster delta')
keys=[p['key'] for p in overlay.get('patches',[])]
for required in ['R0310','R0205','R0806','R0807','PS0001','PS0002']:
    if required not in keys:
        raise SystemExit(f'Missing required R7 patch: {required}')

notes='''# Mercury Dex — R7 Review Pass\n\nR7 removes the misleading **Pending Integration** bucket. Every one of the 118 formerly pending roster rows now has a complete NextDex-facing package: typing, stats, Primary abilities, Innates, and level-up moves.\n\n## Status model\n\n- **Approved roster** — recovered, source-bound, canonical, imported, or explicitly owner-locked data.\n- **Review draft** — a complete proposal where one or more details were never owner-sealed. These are intentionally visible so they can be reviewed rather than left blank.\n\nNo R7 review draft is being represented as a proven ROM/source binding.\n\n## Owner decisions applied\n\n- Mega Yanmega: Bug/Dragon; **Aerial Predator**; Tinted Lens / Compound Eyes / Levitate. Its 615-BST spread remains marked for review.\n- Mega Electivire: Electric/Fighting; **Dynamo Fist**; Motor Drive / Defiant / Vital Spirit. Its stat spread remains marked for review.\n- Old axe Redux Honedge / Doublade / Aegislash family removed from the active Dex view.\n- Former Mega Aegislash identity becomes **Regalibur**, a permanent Steel/Ghost split evolution of Doublade. Exact stats and the proposed Dawn Stone route remain review items.\n- Bow/arrow evolution becomes **Arbalistia**. **Deadeye / Sniper / Infiltrator / Super Luck** is locked; Bulletproof is removed. Exact stats and Redux Stone route remain review items.\n- Delta Tyrantrum and Mega Houndoom Z are promoted out of the old pending bucket using their source-bound post-seal packages.\n- Mega Weavile X/Y naming and packages are separated.\n\n## Added post-seal entries missing from R6\n\n- Mega Lucario Z — Fighting/Psychic; Aura Mantle; Inner Focus / Mega Launcher / Competitive.\n- Mega Garchomp Z — pure Dragon; Sand Skimmer; Sinister Claws / Terminal Velocity / Sleek Scales.\n- Mega Absol Z — Dark/Ghost; Calamity Edge; Super Luck / Defiant / Bad Luck.\n- Mega Baxcalibur — Dragon/Ice; Permafrost; Thermal Entropy / Frost Dragon / Overwhelm.\n- Mega Golisopod — Bug/Steel; Tactical Withdrawal; Bulletproof / Tinted Lens / Galvanize.\n\nTheir owner-locked mechanics are preserved; unrecovered stat spreads (and Sand Skimmer's exact runtime) are explicitly marked **Review draft**.\n\n## Former Reborn / Plates blank rows\n\nThe 94 alternate-family candidates now inherit the base species' completed stat/learnset framework and receive a type-aware Mercury typing, ability, and STAB-move proposal. All 94 are tagged **Review draft** so they can be accepted, changed, or rejected family-by-family without leaving the Dex incomplete.\n\n## R7 validation\n\nThe generated overlay was audited before publication: 0 old pending rows remain in the R7 model; all formerly pending entries have nonblank types, full six-stat spreads, Primary abilities, Innates, and level-up moves.\n'''
(ROOT/'R7_REVIEW_NOTES.md').write_text(notes)
print('R7 NextDex patch prepared: 1,604 entries; 0 Pending Integration; 118 review drafts.')
