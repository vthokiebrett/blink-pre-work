(function(){
  // ===== Injected by build.py — do not edit here; edit the brand file + SHARED_ENDPOINT =====
  var FORM_NAME = __FORM_NAME__;   // routes to a tab of this name in the shared Google Sheet
  var ENDPOINT  = __ENDPOINT__;    // shared Apps Script /exec URL (same for every brand)
  var KEY       = __STORAGE_KEY__; // localStorage key (per brand, so brands don't collide)
  var LABELS    = __LABELS__;      // { fieldName: "1.1 full question text", ... }
  // =========================================================================================

  var form = document.querySelector('form');
  var note = document.getElementById('saveNote');
  var fields = Array.prototype.slice.call(form.querySelectorAll('textarea, input'));
  var timer;

  function load(){
    var raw; try { raw = localStorage.getItem(KEY); } catch(e){ return; }
    if(!raw) return;
    var data; try { data = JSON.parse(raw); } catch(e){ return; }
    fields.forEach(function(f){ if(f.name && data[f.name] != null) f.value = data[f.name]; });
  }
  function collect(){
    var data = {};
    fields.forEach(function(f){ if(f.name) data[f.name] = f.value; });
    return data;
  }
  function save(){
    try { localStorage.setItem(KEY, JSON.stringify(collect())); } catch(e){}
    flash('<b>Saved ✓</b> · kept in this browser');
  }
  function flash(html, sticky){
    if(!note) return; note.innerHTML = html; clearTimeout(timer);
    if(!sticky) timer = setTimeout(function(){ note.textContent = 'Your answers save automatically in this browser.'; }, 1800);
  }
  load();
  fields.forEach(function(f){ f.addEventListener('input', save); });

  // Submit -> Google Sheet (Apps Script web app)
  var submit = document.getElementById('submitBtn');
  if(submit) submit.addEventListener('click', function(){
    if(ENDPOINT.indexOf('http') !== 0){ alert('This form is not connected yet. Ask your Blink strategist for the live link.'); return; }
    var d = collect();
    var payload = { _form: FORM_NAME, _submitted_at: new Date().toISOString() };
    Object.keys(LABELS).forEach(function(k){ payload[LABELS[k]] = d[k] || ''; });
    submit.disabled = true; flash('Submitting…', true);
    fetch(ENDPOINT, { method:'POST', mode:'no-cors', headers:{'Content-Type':'text/plain;charset=utf-8'}, body: JSON.stringify(payload) })
      .then(function(){ window.location.href = 'submitted/'; })
      .catch(function(){ submit.disabled = false; flash('Could not submit — check your connection and try again, or use “Download a copy”.', true); });
  });

  // Fallback: download a CSV copy
  var dl = document.getElementById('downloadBtn');
  if(dl) dl.addEventListener('click', function(){
    save();
    var d = collect();
    var rows = [['Question','Answer']];
    Object.keys(LABELS).forEach(function(k){ rows.push([LABELS[k], d[k] || '']); });
    var csv = rows.map(function(r){ return r.map(function(c){ return '"' + String(c).replace(/"/g,'""') + '"'; }).join(','); }).join('\r\n');
    var blob = new Blob(['﻿'+csv], {type:'text/csv;charset=utf-8'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = FORM_NAME.replace(/[^A-Za-z0-9]+/g,'-') + '-Discovery-PreWork.csv';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  });

  var clr = document.getElementById('clearBtn');
  if(clr) clr.addEventListener('click', function(){
    if(!confirm('Clear all your answers on this device? This cannot be undone.')) return;
    try { localStorage.removeItem(KEY); } catch(e){}
    fields.forEach(function(f){ f.value = ''; });
    if(note) note.textContent = 'Cleared. Your answers save automatically in this browser.';
  });
})();
