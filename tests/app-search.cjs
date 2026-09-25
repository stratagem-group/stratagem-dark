const assert = require('node:assert/strict');
const search = require('../desktop/runtime/shell/services/AppSearch.js');
const foot = {id:'foot',name:'Foot'};
const rows=search.sortedEntries([...Array(12).fill(foot),{id:'foot.desktop',name:'Foot'},{id:'firefox',name:'Firefox'},{id:'hidden',name:'Hidden',noDisplay:true}], '', ()=>false);
assert.deepEqual(rows.map(r=>r.entry.id),['firefox','foot']);
assert.equal(search.sortedEntries([foot], 'fire', ()=>false).length,0);
assert.equal(search.sortedEntries([foot], '', ()=>true).length,0);
console.log('Application deduplication and visibility checks passed');
