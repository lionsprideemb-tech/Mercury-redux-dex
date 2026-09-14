'use strict';
const $ = (q, el=document) => el.querySelector(q);
const $$ = (q, el=document) => [...el.querySelectorAll(q)];
const state = { data:[], meta:{}, filtered:[], shown:0, pageSize:96, status:'all', query:'', type:'', group:'', source:'', cls:'', sort:'dex', favorites:new Set(JSON.parse(localStorage.getItem('mercuryDexFavorites')||'[]')), compare:[] };
const statKeys=[['hp','HP'],['atk','Atk'],['def','Def'],['spa','SpA'],['spd','SpD'],['spe','Spe']];
const escapeHtml=s=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const typeClass=t=>`type-${String(t).replace(/[^A-Za-z]/g,'')}`;
const typeBadge=t=>`<span class="type-badge" style="background:var(--${typeClass(t)},#777)">${escapeHtml(t)}</span>`;
const displayId=p=>p.nationalDex?`#${String(p.nationalDex).padStart(4,'0')}`:(p.reviewId||p.constant||'Mercury');
const hasSprite=p=>Boolean(p.spriteAtlas);
const atlasStyle=p=>{const a=p.spriteAtlas;if(!a)return '';return `background-image:url('${a.sheet}');background-position:-${a.x}px -${a.y}px;`;};
const spriteMarkup=(p,cls='',label='')=>p.spriteAtlas?`<span class="atlas-sprite ${cls}" role="img" aria-label="${escapeHtml(label||p.displayName||p.name)} sprite" style="${atlasStyle(p)}"></span>`:'';
async function fetchBase64Bytes(url){
  const res=await fetch(url);
  if(!res.ok) throw new Error(`HTTP ${res.status} loading ${url}`);
  const b64=(await res.text()).replace(/\s+/g,'');
  const raw=atob(b64), out=new Uint8Array(raw.length);
  for(let i=0;i<raw.length;i++) out[i]=raw.charCodeAt(i);
  return out;
}
async function gunzipJson(url){
  const u8=await fetchBase64Bytes(url);
  if(u8[0]===0x1f&&u8[1]===0x8b){
    if(!('DecompressionStream' in window)) throw new Error('This browser cannot open the compressed Pokédex database. Please use a current Safari, Chrome, Edge, or Firefox version.');
    const stream=new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'));
    return await new Response(stream).json();
  }
  return JSON.parse(new TextDecoder().decode(u8));
}
async function loadPokedexPayload(){
  const idxRes=await fetch('data/pokedex/index.json');
  if(!idxRes.ok) throw new Error(`HTTP ${idxRes.status} loading Pokédex index`);
  const idx=await idxRes.json();
  const parts=await Promise.all((idx.shards||[]).map(name=>gunzipJson(`data/pokedex/${name}`)));
  const pokemon=parts.flatMap(x=>x.pokemon||[]);
  await hydrateSpriteAtlases(pokemon);
  return {meta:idx.meta||{},pokemon};
}

async function hydrateSpriteAtlases(pokemon){
  const sheets=[...new Set(pokemon.map(p=>p.spriteAtlas?.sheet).filter(Boolean))];
  const entries=await Promise.all(sheets.map(async sheet=>{
    const bytes=await fetchBase64Bytes(`${sheet}.b64`);
    const url=URL.createObjectURL(new Blob([bytes],{type:'image/webp'}));
    return [sheet,url];
  }));
  const map=new Map(entries);
  pokemon.forEach(p=>{
    const sheet=p.spriteAtlas?.sheet;
    if(sheet&&map.has(sheet)) p.spriteAtlas.sheet=map.get(sheet);
  });
}

const isCurrent=p=>!p.planned;

async function boot(){
  try{
    const payload=await loadPokedexPayload(); state.data=payload.pokemon; state.meta=payload.meta||{};
    hydrateFilters(); bindEvents(); updateCounts(); applyFilters(); openFromHash();
    $('#headerMeta').textContent=`${state.meta.rosterCount?.toLocaleString()||state.data.length.toLocaleString()} entries · ${state.meta.sourceAuthority||'R6 authority'}`;
    $('#sourceBoundCount').textContent=(state.meta.sourceBoundCount||state.data.filter(isCurrent).length).toLocaleString();
    $('#spriteCount').textContent=(state.meta.spriteCount||state.data.filter(hasSprite).length).toLocaleString();
  }catch(err){
    $('#dexGrid').innerHTML=`<div class="empty-state"><h2>Could not load Pokédex data</h2><p>${escapeHtml(err.message)}. GitHub Pages or a local web server is required.</p></div>`;
  }
}
function hydrateFilters(){
  const types=[...new Set(state.data.flatMap(p=>p.types||[]))].sort();
  const sources=[...new Set(state.data.map(p=>p.source).filter(Boolean))].sort();
  const classes=[...new Set(state.data.map(p=>p.classification).filter(Boolean))].sort();
  $('#typeFilter').insertAdjacentHTML('beforeend',types.map(x=>`<option>${escapeHtml(x)}</option>`).join(''));
  $('#sourceFilter').insertAdjacentHTML('beforeend',sources.map(x=>`<option>${escapeHtml(x)}</option>`).join(''));
  $('#classFilter').insertAdjacentHTML('beforeend',classes.map(x=>`<option>${escapeHtml(x)}</option>`).join(''));
}
function bindEvents(){
  $('#searchInput').addEventListener('input',e=>{state.query=e.target.value.trim().toLowerCase();applyFilters();});
  $('#typeFilter').addEventListener('change',e=>{state.type=e.target.value;applyFilters();});
  $('#groupFilter').addEventListener('change',e=>{state.group=e.target.value;applyFilters();});
  $('#sourceFilter').addEventListener('change',e=>{state.source=e.target.value;applyFilters();});
  $('#classFilter').addEventListener('change',e=>{state.cls=e.target.value;applyFilters();});
  $('#sortSelect').addEventListener('change',e=>{state.sort=e.target.value;applyFilters();});
  $$('#statusTabs .tab').forEach(b=>b.addEventListener('click',()=>{state.status=b.dataset.status; $$('#statusTabs .tab').forEach(x=>x.classList.toggle('active',x===b));applyFilters();}));
  $('#clearBtn').addEventListener('click',resetFilters);
  $('#filterToggle').addEventListener('click',()=>$('#filtersPanel').classList.toggle('open'));
  $('#loadMoreBtn').addEventListener('click',()=>{state.shown+=state.pageSize;renderCards();});
  $('#detailClose').addEventListener('click',closeDetail); $('#detailBackdrop').addEventListener('click',closeDetail);
  $('#compareClear').addEventListener('click',()=>{state.compare=[];renderCompareTray();});
  $('#compareOpen').addEventListener('click',openCompare); $('#compareClose').addEventListener('click',()=>$('#compareDialog').close());
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!/input|select|textarea/i.test(document.activeElement.tagName)){e.preventDefault();$('#searchInput').focus();} if(e.key==='Escape') closeDetail();});
  window.addEventListener('hashchange',openFromHash);
}
function resetFilters(){
  state.query=state.type=state.group=state.source=state.cls=''; state.status='all';state.sort='dex';
  $('#searchInput').value=''; $('#typeFilter').value='';$('#groupFilter').value='';$('#sourceFilter').value='';$('#classFilter').value='';$('#sortSelect').value='dex';
  $$('#statusTabs .tab').forEach(b=>b.classList.toggle('active',b.dataset.status==='all')); applyFilters();
}
function updateCounts(){
  $('#tabAllCount').textContent=state.data.length.toLocaleString();
  $('#tabCurrentCount').textContent=state.data.filter(isCurrent).length.toLocaleString();
  $('#tabPlannedCount').textContent=state.data.filter(p=>p.planned).length.toLocaleString();
  $('#tabFavoriteCount').textContent=state.favorites.size?state.favorites.size.toLocaleString():'';
}
function applyFilters(){
  let a=state.data.filter(p=>{
    if(state.status==='current'&&!isCurrent(p))return false;
    if(state.status==='planned'&&!p.planned)return false;
    if(state.status==='favorites'&&!state.favorites.has(p.key))return false;
    if(state.query&&!p.searchText?.includes(state.query))return false;
    if(state.type&&!(p.types||[]).includes(state.type))return false;
    if(state.group&&p.rosterGroup!==state.group)return false;
    if(state.source&&p.source!==state.source)return false;
    if(state.cls&&p.classification!==state.cls)return false;
    return true;
  });
  const nat=p=>p.nationalDex??99999, id=p=>p.id??999999;
  a.sort((x,y)=>{
    if(state.sort==='name')return (x.displayName||x.name).localeCompare(y.displayName||y.name);
    if(state.sort==='bst-desc')return (y.bst??-1)-(x.bst??-1)||nat(x)-nat(y);
    if(state.sort==='bst-asc')return (x.bst??9999)-(y.bst??9999)||nat(x)-nat(y);
    if(state.sort==='newest')return (x.rosterGroup==='Addition'?0:1)-(y.rosterGroup==='Addition'?0:1)||id(x)-id(y);
    return nat(x)-nat(y)||id(x)-id(y)||(x.reviewId||'').localeCompare(y.reviewId||'');
  });
  state.filtered=a;state.shown=state.pageSize;renderCards();
}
function renderCards(){
  const grid=$('#dexGrid'), tmpl=$('#cardTemplate'); grid.innerHTML='';
  const visible=state.filtered.slice(0,state.shown), frag=document.createDocumentFragment();
  visible.forEach(p=>{
    const node=tmpl.content.firstElementChild.cloneNode(true); node.dataset.key=p.key; node.classList.toggle('pending',!!p.planned);
    $('.card-id',node).textContent=displayId(p);
    $('.card-name',node).textContent=p.displayName||p.name;
    $('.type-row',node).innerHTML=(p.types||[]).map(typeBadge).join('')||'<span class="source-pill">Type pending</span>';
    $('.card-status',node).textContent=p.planned?'Pending integration':'Current source';
    $('.card-bst',node).textContent=p.bst?`BST ${p.bst}`:'BST —';
    const well=$('.sprite-well',node), ph=$('.sprite-placeholder',node);
    if(p.spriteAtlas){well.insertAdjacentHTML('afterbegin',spriteMarkup(p,'card-sprite'));ph.style.display='none';}else{ph.style.display='grid';}
    const fav=$('.favorite-btn',node);fav.classList.toggle('active',state.favorites.has(p.key));fav.textContent=state.favorites.has(p.key)?'★':'☆';
    fav.addEventListener('click',e=>{e.stopPropagation();toggleFavorite(p.key);});
    node.addEventListener('click',()=>openDetail(p)); node.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openDetail(p);}}); frag.append(node);
  });
  grid.append(frag); $('#resultCount').textContent=state.filtered.length.toLocaleString(); $('#emptyState').hidden=state.filtered.length>0;
  const more=state.shown<state.filtered.length; $('#loadMoreBtn').hidden=!more; if(more)$('#loadMoreBtn').textContent=`Load ${Math.min(state.pageSize,state.filtered.length-state.shown)} more`;
}
function toggleFavorite(key){
  state.favorites.has(key)?state.favorites.delete(key):state.favorites.add(key);localStorage.setItem('mercuryDexFavorites',JSON.stringify([...state.favorites]));updateCounts();renderCards();
}
function abilityCards(p){
  const cards=[];
  (p.primaryAbilities||[]).forEach((a,i)=>cards.push(`<div class="ability-card ${p.primaryLocked?'locked':''}"><div class="slot">Primary ${i+1}${p.primaryLocked?' · locked':''}</div><h4>${escapeHtml(a.name)}</h4><p>${escapeHtml(a.description||'Description pending.')}</p></div>`));
  (p.innates||[]).forEach((a,i)=>cards.push(`<div class="ability-card"><div class="slot">Innate ${i+1}</div><h4>${escapeHtml(a.name)}</h4><p>${escapeHtml(a.description||'Description pending.')}</p></div>`));
  return cards.length?cards.join(''):'<p class="detail-description">Ability package is pending source integration for this approved entry.</p>';
}
function statMarkup(p){
  const rows=statKeys.map(([k,n])=>{const v=p.stats?.[k];const pct=v==null?0:Math.min(100,(v/180)*100);return `<div class="stat-row"><span class="stat-name">${n}</span><span class="stat-value">${v??'—'}</span><div class="stat-track"><div class="stat-fill" style="width:${pct}%"></div></div></div>`}).join('');
  return `<div class="stat-grid">${rows}</div><div class="bst-line"><span>Base Stat Total</span><strong>${p.bst??'Pending'}</strong></div>`;
}
function movesMarkup(p){
 const moves=p.levelUpMoves||[]; if(!moves.length)return '<p class="detail-description">Level-up learnset is not source-bound for this approved entry yet.</p>';
 return `<table class="move-table"><thead><tr><th>Level</th><th>Move</th></tr></thead><tbody>${moves.map(m=>`<tr><td>${escapeHtml(m.level)}</td><td>${escapeHtml(m.move)}</td></tr>`).join('')}</tbody></table>`;
}
function evoMarkup(p){
 const e=p.evolutions||[]; if(!e.length)return '<p class="detail-description">No further evolution is listed in the current source entry.</p>';
 return `<div class="evo-list">${e.map(x=>`<div class="evo-item"><strong>${escapeHtml(x.target?.replace(/^SPECIES_/,'').replaceAll('_',' ')||'Unknown')}</strong><span class="evo-method">${escapeHtml(x.method||'')} ${escapeHtml(x.param||'')}</span></div>`).join('')}</div>`;
}
function openDetail(p){
  const c=$('#detailContent');
  const sourceAb=(p.sourceAbilities||[]).map(a=>escapeHtml(a.name)).join(' · ')||'—';
  c.innerHTML=`<div class="detail-content-wrap">
    <div class="detail-hero"><div class="detail-sprite-well">${p.spriteAtlas?spriteMarkup(p,'detail-sprite'):'<div class="sprite-placeholder" style="display:grid">?</div>'}</div><div>
      <div class="detail-id">${escapeHtml(displayId(p))}</div><h2 class="detail-title">${escapeHtml(p.displayName||p.name)}</h2><div class="detail-tags">${(p.types||[]).map(typeBadge).join('')}<span class="status-pill ${p.planned?'pending':'current'}">${p.planned?'Pending integration':'Current source'}</span></div>
      <div class="detail-actions"><button class="secondary-btn" id="favoriteDetail" type="button">${state.favorites.has(p.key)?'★ Favorited':'☆ Favorite'}</button><button class="secondary-btn" id="compareAdd" type="button">+ Compare</button><button class="secondary-btn" id="copyLink" type="button">Copy link</button></div>
    </div></div>
    <section class="detail-section"><h3 class="section-title">Base stats</h3>${statMarkup(p)}</section>
    <section class="detail-section"><h3 class="section-title">Primary abilities + Innates</h3><div class="ability-grid">${abilityCards(p)}</div>${p.sourceAbilities?.length?`<p class="detail-description"><strong>Original/source ability slots:</strong> ${sourceAb}</p>`:''}</section>
    ${p.description?`<section class="detail-section"><h3 class="section-title">Pokédex entry</h3><p class="detail-description">${escapeHtml(p.description)}</p></section>`:''}
    <section class="detail-section"><h3 class="section-title">Level-up moves</h3>${movesMarkup(p)}</section>
    <section class="detail-section"><h3 class="section-title">Evolution / progression</h3>${evoMarkup(p)}</section>
    <section class="detail-section"><h3 class="section-title">Mercury authority</h3><dl class="provenance-grid">
      <dt>Roster</dt><dd>${escapeHtml(p.rosterGroup)}</dd><dt>Classification</dt><dd>${escapeHtml(p.classification||'—')}</dd><dt>Source</dt><dd>${escapeHtml(p.source||'—')}</dd><dt>Binding</dt><dd>${escapeHtml(p.bindingStatus||'—')}</dd><dt>Source constant</dt><dd>${escapeHtml(p.constant||'Not bound yet')}</dd><dt>Review ID</dt><dd>${escapeHtml(p.reviewId||'—')}</dd>${p.basePokemon?`<dt>Base identity</dt><dd>${escapeHtml(p.basePokemon)}</dd>`:''}${p.notes?`<dt>Notes</dt><dd>${escapeHtml(p.notes)}</dd>`:''}
    </dl></section>
  </div>`;
  $('#favoriteDetail').addEventListener('click',()=>{toggleFavorite(p.key);$('#favoriteDetail').textContent=state.favorites.has(p.key)?'★ Favorited':'☆ Favorite';});
  $('#compareAdd').addEventListener('click',()=>addCompare(p));
  $('#copyLink').addEventListener('click',async()=>{const url=`${location.href.split('#')[0]}#${encodeURIComponent(p.key)}`;try{await navigator.clipboard.writeText(url);$('#copyLink').textContent='Copied';setTimeout(()=>$('#copyLink').textContent='Copy link',1200);}catch{location.hash=encodeURIComponent(p.key);}});
  $('#detailBackdrop').hidden=false;$('#detailPanel').classList.add('open');$('#detailPanel').setAttribute('aria-hidden','false');document.body.classList.add('panel-open');
  if(location.hash!==`#${encodeURIComponent(p.key)}`)history.replaceState(null,'',`#${encodeURIComponent(p.key)}`);
}
function closeDetail(){
 if(!$('#detailPanel').classList.contains('open'))return;$('#detailPanel').classList.remove('open');$('#detailPanel').setAttribute('aria-hidden','true');$('#detailBackdrop').hidden=true;document.body.classList.remove('panel-open');history.replaceState(null,'',location.pathname+location.search);
}
function openFromHash(){
 const key=decodeURIComponent(location.hash.slice(1));if(!key)return;const p=state.data.find(x=>x.key===key||x.constant===key||x.reviewId===key);if(p)openDetail(p);
}
function addCompare(p){
 if(state.compare.some(x=>x.key===p.key))return;if(state.compare.length>=2)state.compare.shift();state.compare.push(p);renderCompareTray();
}
function renderCompareTray(){
 const tray=$('#compareTray');tray.hidden=!state.compare.length;$('#compareSlots').innerHTML=state.compare.map(p=>`<div class="compare-chip">${p.spriteAtlas?spriteMarkup(p,'compare-chip-sprite'):''}<span>${escapeHtml(p.displayName||p.name)}</span></div>`).join('');$('#compareOpen').disabled=state.compare.length<2;
}
function openCompare(){
 if(state.compare.length<2)return;const [a,b]=state.compare;
 const abilityNames=p=>[...(p.primaryAbilities||[]).map(x=>x.name),...(p.innates||[]).map(x=>x.name)].join(', ')||'Pending';
 const row=(label,av,bv)=>`<tr><th>${label}</th><td>${av}</td><td>${bv}</td></tr>`;
 $('#compareContent').innerHTML=`<h2>Compare</h2><div class="compare-head"><div></div>${[a,b].map(p=>`<div class="compare-name">${p.spriteAtlas?spriteMarkup(p,'compare-name-sprite'):''}<h3>${escapeHtml(p.displayName||p.name)}</h3><div>${(p.types||[]).map(typeBadge).join(' ')}</div></div>`).join('')}</div><table class="compare-table"><tbody>
 ${row('BST',a.bst??'—',b.bst??'—')}${statKeys.map(([k,n])=>row(n,a.stats?.[k]??'—',b.stats?.[k]??'—')).join('')}${row('Primary + Innates',escapeHtml(abilityNames(a)),escapeHtml(abilityNames(b)))}${row('Source',escapeHtml(a.source||'—'),escapeHtml(b.source||'—'))}${row('Status',a.planned?'Pending':'Current',b.planned?'Pending':'Current')}
 </tbody></table>`;$('#compareDialog').showModal();
}
boot();
