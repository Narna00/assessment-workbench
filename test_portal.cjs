// Dependency-free unit tests for the portal's DOM rendering/filtering logic.
// This is a minimal DOM harness, not a browser layout or accessibility audit.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, 'portal.html'), 'utf8');
const json = source.match(/<script id="catalog" type="application\/json">([\s\S]*?)<\/script>/)[1];
const program = source.match(/<\/script><script>([\s\S]*?)<\/script>/)[1];
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.textContent=''; this.value=''; this.events={}; }
  appendChild(node) { this.children.push(node); }
  replaceChildren() { this.children=[]; }
  addEventListener(name, handler) { this.events[name]=handler; }
}
const elements=Object.fromEntries(['catalog','cards','q','domain','count'].map(id=>[id,new Element(id)]));
elements.catalog.textContent=json;
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
vm.runInNewContext(program,{document,JSON},{timeout:2000});
assert.equal(elements.cards.children.length,42);
elements.domain.value='web'; elements.domain.events.change();
assert.equal(elements.cards.children.length,12);
elements.domain.value='ad'; elements.domain.events.change();
assert.equal(elements.cards.children.length,10);
elements.q.value='no-such-case-98765'; elements.q.events.input();
assert.equal(elements.cards.children.length,0);
elements.domain.value=''; elements.q.value='WEB-01'; elements.q.events.input();
assert.equal(elements.cards.children.length,1);
assert.equal(elements.count.textContent,'1 of 42 test cases');
console.log('Portal DOM harness: all-domain, web, AD, empty-result, and exact-ID filters passed');
