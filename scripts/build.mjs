#!/usr/bin/env node
// birdwork.ai build — zero dependencies (plain `node scripts/build.mjs`).
//
//   src/data/site.yaml   human-editable content + micro-layout manifest
//   src/template.html    page shell with {{tokens}}, {{#each}}/{{#if}}, {{> partials}}
//   src/partials/*.html  diagram + nav partials
//   -> index.html        rendered output
//
// Flags:  --check   validate + render to memory, write nothing (exit 1 on any error)
//         --quiet   only print "build: ok"
//
// Every failure is fatal and named, so a typo in the YAML can never reach main.

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'src');
const PARTIAL_DIR = join(SRC, 'partials');
const OUT = join(ROOT, 'index.html');

const argv = new Set(process.argv.slice(2));
const CHECK = argv.has('--check');
const QUIET = argv.has('--quiet') || CHECK;

const SPACING = { '0': '0', xs: '0.5rem', sm: '1rem', md: '1.5rem', lg: '2.25rem', xl: '3.5rem', '2xl': '5rem' };
const SPACING_STEPS = Object.keys(SPACING);
const LAYOUT_PROPS = ['m', 'mt', 'mb', 'ml', 'mr', 'p', 'pt', 'pb', 'pl', 'pr', 'py', 'px', 'gap'];
const CSS_LEN = /^(0|\d+(\.\d+)?(rem|em|px|%|ch|vw|vh))$/;

class BuildError extends Error {}

/* ------------------------------------------------------------------ YAML ---
   Deliberately small: indentation maps, `- ` lists, inline [a, b] lists, quoted
   or bare one-line scalars. Enough for a 2-3 level manifest, no surprises.     */

function parseYaml(text, file) {
  const lines = text.split(/\r?\n/);
  const root = {};
  const stack = [{ indent: -1, node: root, key: null }];

  lines.forEach((raw, i) => {
    const lineNo = i + 1;
    if (!raw.trim() || /^\s*#/.test(raw)) return;

    const indent = raw.match(/^\s*/)[0].replace(/\t/g, '  ').length;
    let rest = raw.trim();

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) stack.pop();
    const top = stack[stack.length - 1];
    if (indent <= top.indent) throw new BuildError(`${file}:${lineNo} bad indentation`);

    if (rest.startsWith('- ') || rest === '-') {
      rest = rest.slice(1).trim();
      if (!Array.isArray(top.node)) throw new BuildError(`${file}:${lineNo} list item outside a list`);
      if (!rest) {
        const obj = {};
        top.node.push(obj);
        stack.push({ indent, node: obj, key: null });
        return;
      }
      const kv = splitKey(rest, file, lineNo);
      if (kv) {
        const obj = { [kv.key]: scalar(kv.value, file, lineNo) };
        top.node.push(obj);
        stack.push({ indent, node: obj, key: null });
      } else {
        top.node.push(scalar(rest, file, lineNo));
      }
      return;
    }

    const kv = splitKey(rest, file, lineNo);
    if (!kv) throw new BuildError(`${file}:${lineNo} expected "key: value"`);
    const { key, value } = kv;

    if (value === '') {
      const next = nextMeaningful(lines, i);
      const makeList = next !== null && next.trim().startsWith('-');
      const node = makeList ? [] : {};
      if (key in top.node) throw new BuildError(`${file}:${lineNo} duplicate key "${key}"`);
      top.node[key] = node;
      stack.push({ indent, node, key });
      return;
    }

    if (key in top.node) throw new BuildError(`${file}:${lineNo} duplicate key "${key}"`);
    top.node[key] = scalar(value, file, lineNo);
  });

  return root;
}

function nextMeaningful(lines, from) {
  for (let i = from + 1; i < lines.length; i++) {
    const l = lines[i];
    if (!l.trim() || /^\s*#/.test(l)) continue;
    return l;
  }
  return null;
}

function splitKey(s, file, lineNo) {
  const m = s.match(/^([A-Za-z0-9_.\-]+):(?:\s+(.*))?$/);
  if (!m) return null;
  return { key: m[1], value: (m[2] ?? '').trim() };
}

function scalar(v, file, lineNo) {
  if (/^\[.*\]$/.test(v)) {
    const inner = v.slice(1, -1).trim();
    if (!inner) return [];
    return inner.split(',').map((p) => scalar(p.trim(), file, lineNo));
  }
  if (/^\{.*\}$/.test(v)) {
    const inner = v.slice(1, -1).trim();
    const obj = {};
    if (!inner) return obj;
    for (const part of inner.split(',')) {
      const kv = splitKey(part.trim(), file, lineNo);
      if (!kv) throw new BuildError(`${file}:${lineNo} bad inline map entry "${part.trim()}"`);
      if (kv.key in obj) throw new BuildError(`${file}:${lineNo} duplicate inline key "${kv.key}"`);
      obj[kv.key] = scalar(kv.value, file, lineNo);
    }
    return obj;
  }
  const q = v.match(/^(["'])(.*)\1$/s);
  if (q) return q[1] === '"' ? q[2].replace(/\\n/g, '\n').replace(/\\"/g, '"') : q[2].replace(/\\'/g, "'");
  if (/^(true|false)$/.test(v)) return v === 'true';
  if (/^-?\d+$/.test(v)) return Number(v);
  const hash = v.indexOf(' #');
  return (hash === -1 ? v : v.slice(0, hash)).trim();
}

/* --------------------------------------------------------------- template ---
   Nodes: text | var | join | include | each | if.  Unresolved vars throw, so a
   renamed key fails the build instead of silently rendering blank.            */

function parseNodes(tpl, file) {
  const nodes = [];
  let i = 0;
  while (i < tpl.length) {
    const open = tpl.indexOf('{{', i);
    if (open === -1) { nodes.push({ t: 'text', v: tpl.slice(i) }); break; }
    if (open > i) nodes.push({ t: 'text', v: tpl.slice(i, open) });
    const close = tpl.indexOf('}}', open);
    if (close === -1) throw new BuildError(`${file}: unclosed {{ at ${open}`);
    const body = tpl.slice(open + 2, close).trim();
    i = close + 2;

    if (body.startsWith('#each ') || body.startsWith('#if ')) {
      const kind = body.startsWith('#each ') ? 'each' : 'if';
      const path = body.slice(kind === 'each' ? 6 : 4).trim();
      const end = findClose(tpl, i, kind, file);
      const kids = parseNodes(tpl.slice(i, end.at), file);
      i = end.at + end.len;
      nodes.push({ t: kind, path, kids });
      continue;
    }
    if (body.startsWith('/')) continue;

    const inc = body.match(/^>\s*([A-Za-z0-9_\-./]+)$/);
    if (inc) { nodes.push({ t: 'include', name: inc[1], file }); continue; }

    const jn = body.match(/^join\s+([A-Za-z0-9_.]+)\s+(.*)$/);
    if (jn) { nodes.push({ t: 'join', path: jn[1], sep: unquote(jn[2]) }); continue; }

    if (!/^[A-Za-z0-9_.]+$/.test(body)) throw new BuildError(`${file}: bad token {{${body}}}`);
    nodes.push({ t: 'var', path: body, file });
  }
  return nodes;
}

function unquote(s) {
  const m = s.trim().match(/^(["'])(.*)\1$/s);
  return m ? m[2] : s.trim();
}

function findClose(tpl, from, kind, file) {
  let depth = 1, i = from;
  while (i < tpl.length) {
    const open = tpl.indexOf('{{', i);
    if (open === -1) break;
    const close = tpl.indexOf('}}', open);
    if (close === -1) break;
    const body = tpl.slice(open + 2, close).trim();
    if (body.startsWith(`#${kind} `)) depth++;
    else if (body === `/${kind}`) { depth--; if (depth === 0) return { at: open, len: `{{/${kind}}}`.length }; }
    i = close + 2;
  }
  throw new BuildError(`${file}: missing {{/${kind}}}`);
}

function lookup(path, ctx) {
  if (path === '.' || path === 'this') return ctx['.'];
  let cur = ctx;
  for (const part of path.split('.')) {
    if (cur == null || typeof cur !== 'object' || !(part in cur)) return undefined;
    cur = cur[part];
  }
  return cur;
}

function render(nodes, ctx, partials, out) {
  for (const n of nodes) {
    if (n.t === 'text') { out.push(n.v); continue; }
    if (n.t === 'var') {
      const val = lookup(n.path, ctx);
      if (val === undefined) throw new BuildError(`${n.file || 'template'}: unresolved {{${n.path}}}`);
      out.push(String(val));
      continue;
    }
    if (n.t === 'join') {
      const val = lookup(n.path, ctx);
      if (val === undefined) throw new BuildError(`unresolved {{join ${n.path}}}`);
      if (!Array.isArray(val)) throw new BuildError(`{{join ${n.path}}} needs a list`);
      out.push(val.map(String).join(n.sep));
      continue;
    }
    if (n.t === 'include') {
      const p = partials[n.name];
      if (!p) throw new BuildError(`missing partial "${n.name}"`);
      render(p, ctx, partials, out);
      continue;
    }
    if (n.t === 'if') {
      const val = lookup(n.path, ctx);
      if (Array.isArray(val) ? val.length : Boolean(val)) render(n.kids, ctx, partials, out);
      continue;
    }
    if (n.t === 'each') {
      const val = lookup(n.path, ctx);
      if (!Array.isArray(val)) throw new BuildError(`{{#each ${n.path}}} needs a list`);
      val.forEach((item, idx) => {
        const extra = { '.': item, '@index': idx, '@first': idx === 0, '@last': idx === val.length - 1, this: item };
        const child = typeof item === 'object' && item !== null ? Object.assign({}, ctx, extra, item) : Object.assign({}, ctx, extra);
        render(n.kids, child, partials, out);
      });
      continue;
    }
  }
  return out;
}

/* ----------------------------------------------------------------- layout ---
   layout.<section>.<el>.<prop> -> --<section>-<el>-<prop> on :root.           */

function layoutCss(layout, prefix = [], decls = []) {
  for (const [key, value] of Object.entries(layout || {})) {
    if (value === null || typeof value !== 'object') {
      throw new BuildError(`layout.${[...prefix, key].join('.')}: expected {prop: value}, got "${value}"`);
    }
    // a map whose keys are all layout props is the leaf; otherwise it is a path
    const keys = Object.keys(value);
    if (!keys.length || !keys.every((k) => k === 'show' || LAYOUT_PROPS.includes(k))) {
      layoutCss(value, [...prefix, key], decls);
      continue;
    }
    const name = [...prefix, key].map(slug).join('-');
    const where = [...prefix, key].join('.');
    for (const [prop, raw] of Object.entries(value)) {
      if (prop === 'show') continue;
      if (!LAYOUT_PROPS.includes(prop)) {
        throw new BuildError(`layout.${where}.${prop}: unknown property (use ${LAYOUT_PROPS.join('/')})`);
      }
      decls.push(`  --${name}-${prop}: ${spacingValue(raw, `${where}.${prop}`)};`);
    }
  }
  return prefix.length ? undefined : decls.length ? `:root{\n${decls.join('\n')}\n}` : '';
}

function spacingValue(raw, where) {
  const v = String(raw).trim();
  if (v === '') throw new BuildError(`layout.${where}: empty value`);
  if (SPACING[v] !== undefined) return SPACING[v];
  if (!CSS_LEN.test(v)) {
    throw new BuildError(`layout.${where}: "${v}" is not a token (${SPACING_STEPS.join(', ')}) or a CSS length`);
  }
  return v;
}

const slug = (s) => s.replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, '').toLowerCase();

/* --------------------------------------------------------------- validate ---
   Shape rules — cheap, and they catch the mistakes a text edit actually makes. */

const get = (obj, path) => path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);

export const SECTIONS = ['work', 'cases', 'finops', 'security', 'rd', 'about', 'connect'];
const NAV_SECTIONS = ['cases', 'work', 'finops', 'security', 'rd', 'about', 'connect'];

function validate(data) {
  const need = (cond, msg) => { if (!cond) throw new BuildError(msg); };

  const strFields = [
    'site.full_name', 'site.domain', 'site.email', 'site.location', 'site.linkedin_url',
    'seo.title', 'seo.description', 'hero.h1', 'hero.sub', 'footer.blurb'
  ];
  for (const key of strFields) {
    const val = get(data, key);
    need(typeof val === 'string' && val.length > 0, `required string missing: ${key}`);
  }

  const listMin = {
    'hero.tags': 3, 'nav.links': 6, 'stats.items': 4, 'hero.ctas': 2,
    'work.cards': 3, 'cases.items': 1, 'stack.columns': 3, 'about.paras': 1,
    'about.creds': 1, 'about.ctas': 2, 'connect.ctas': 2, 'rd.meta': 1, 'footer.meta': 1
  };
  for (const key of Object.keys(listMin)) {
    const val = get(data, key);
    need(Array.isArray(val), `required list missing: ${key}`);
    need(val.length >= listMin[key], `${key} needs at least ${listMin[key]} item(s)`);
  }

  // every section: object with a label (label drives heading + navbar)
  for (const sec of SECTIONS) {
    const s = data[sec];
    need(s && typeof s === 'object' && !Array.isArray(s), `section missing: ${sec}`);
    need(typeof s.label === 'string' && s.label, `${sec}.label required`);
    if (s.eyebrow !== undefined) need(typeof s.eyebrow === 'string', `${sec}.eyebrow must be text`);
    if (s.nav_label !== undefined) need(typeof s.nav_label === 'string', `${sec}.nav_label must be text`);
  }

  // every nav link must point at a real section
  for (const link of data.nav.links) {
    need(link.section && NAV_SECTIONS.includes(link.section), `nav.links[].section invalid: ${link.section}`);
    need(typeof link.href === 'string' && link.href.startsWith('#'), `nav.links[].href invalid for ${link.section}`);
  }
  need(data.nav.connect && data.nav.connect.section === 'connect', 'nav.connect.section must be connect');

  // client spans must carry a resolvable SITE key
  for (const item of data.cases.items) {
    need(item.client_fallback, 'cases.items[].client_fallback required');
    if (item.client_key) {
      need(item.client_key.startsWith('client.'), `cases.items[].client_key must start with client.`);
      const ck = item.client_key.slice(7);
      const camel = (x) => Object.fromEntries(Object.entries(x).map(([k, v]) => [k.replace(/_([a-z])/g, (_, c) => c.toUpperCase()), v]));
      need(camel(data.site.clients)[ck] !== undefined, `client_key unresolved: ${item.client_key}`);
    }
    need(['lead', 'full', 'wide'].includes(item.kind), `cases.items[].kind invalid: ${item.kind}`);
  }
  for (const card of data.work.cards) {
    need(card.num && card.title && card.body, 'work.cards[] needs num, title, body');
    need(Array.isArray(card.proof) && card.proof.length, `work.cards[${card.num}].proof needs items`);
  }

  // banned tokens (The Tony Test / anonymization gates)
  const banned = ['Sacred Spaces', 'Docere Noscere', 'Wyzant', 'github.com', 'Ally Logistics', 'GPA'];
  const flat = JSON.stringify(data);
  for (const b of banned) need(!flat.includes(b), `banned token present: ${b}`);
}

// nav labels resolve from the target section: nav_label wins, label is the base.
// derived flags keep the template free of comparison logic.
function prepare(data) {
  data.nav.links.forEach((link) => { link.label = data[link.section].nav_label || data[link.section].label; });
  data.nav.connect.label = data.connect.nav_label || data.connect.label;

  const camel = (s) => s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
  data.site_json = JSON.stringify({
    FULL_NAME: data.site.full_name,
    SITE_DOMAIN: data.site.domain,
    EMAIL: data.site.email,
    LOCATION: data.site.location,
    LINKEDIN_URL: data.site.linkedin_url,
    HEADSHOT_PATH: data.site.headshot_light,
    HEADSHOT_DARK: data.site.headshot_dark,
    CLIENTS: Object.fromEntries(Object.entries(data.site.clients).map(([k, v]) => [camel(k), v]))
  });

  data.cases.items.forEach((item) => {
    item.is_lead = item.kind === 'lead';
    item.is_full = item.kind === 'full';
    item.is_wide = item.kind === 'wide';
  });
  for (const list of [data.hero.ctas, data.about.ctas, data.connect.ctas]) {
    list.forEach((cta) => { if (String(cta.href).startsWith('http')) cta.external = true; });
  }
  return data;
}

/* ------------------------------------------------------------------- main --- */

function loadPartials() {
  const out = {};
  if (!existsSync(PARTIAL_DIR)) return out;
  for (const f of readdirSync(PARTIAL_DIR)) {
    if (!f.endsWith('.html')) continue;
    const name = f.replace(/\.html$/, '');
    out[name] = parseNodes(readFileSync(join(PARTIAL_DIR, f), 'utf8'), `src/partials/${f}`);
  }
  return out;
}

function main() {
  const yamlPath = join(SRC, 'data', 'site.yaml');
  const tplPath = join(SRC, 'template.html');
  const data = prepare(parseYaml(readFileSync(yamlPath, 'utf8'), 'src/data/site.yaml'));
  validate(data);
  data.layout_css = layoutCss(data.layout);

  const partials = loadPartials();
  const nodes = parseNodes(readFileSync(tplPath, 'utf8'), 'src/template.html');
  const html = render(nodes, data, partials, []).join('');

  if (html.length < 20000) throw new BuildError(`rendered output suspiciously small (${html.length} bytes)`);

  if (!CHECK) writeFileSync(OUT, html);
  if (!QUIET) {
    const bytes = Buffer.byteLength(html);
    console.log(CHECK ? `build: ok (${bytes} bytes, not written)` : `build: ok -> index.html (${bytes} bytes)`);
  } else if (CHECK) {
    console.log('build: ok');
  }
}

try {
  main();
} catch (err) {
  console.error(`build: FAIL — ${err.message}`);
  process.exit(1);
}
