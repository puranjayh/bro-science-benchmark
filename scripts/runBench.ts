// BroScienceBench v1.1 — Paper 2 eval harness (RAW models only).
//
// No guardrails, no knowledge injection — just baseline models head-to-head, to
// establish how current models do on the public benchmark. (The system/ablation
// numbers live in runBench.ts / Paper 1.)
//
//   cd mobile
//   npx tsx scripts/runBench_paper2.ts                       # all models, open mode
//   npx tsx scripts/runBench_paper2.ts --mode mcq            # MCQ mode
//   npx tsx scripts/runBench_paper2.ts --model openai/gpt-4o-mini   # single model
//   npx tsx scripts/runBench_paper2.ts --limit 20            # quick smoke test
//   npx tsx scripts/runBench_paper2.ts --split held_out      # held_out | hard | core
//
// Saves a JSON results file to research/results_paper2_<mode>_<ts>.json.
// Reads OPENROUTER_API_KEY from .env.local.

import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const HERE = dirname(fileURLToPath(import.meta.url))
const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
const OR_URL = 'https://openrouter.ai/api/v1/chat/completions'
// Judge defaults to qwen-2.5-72b (neutral — outside all 8 tested families, so no
// self-judging bias). Override with --judge. Validate labels with judge_kappa.py.
const JUDGE_MODEL = process.argv.includes('--judge')
  ? process.argv[process.argv.indexOf('--judge') + 1]
  : 'qwen/qwen-2.5-72b-instruct' // neutral: outside all tested families

// ── Models to evaluate (Groq slugs go direct; everything else via OpenRouter) ─
const MODELS: Record<string, { label: string; via: 'groq' | 'openrouter' }> = {
  // open
  'meta-llama/llama-3.1-8b-instruct': { label: 'Llama 3.1 8B', via: 'openrouter' },
  'meta-llama/llama-3.3-70b-instruct': { label: 'Llama 3.3 70B', via: 'openrouter' },
  'deepseek/deepseek-chat-v3.1': { label: 'DeepSeek V3.1', via: 'openrouter' },
  // closed — small / fast
  'openai/gpt-4o-mini': { label: 'GPT-4o mini', via: 'openrouter' },
  'google/gemini-3.5-flash': { label: 'Gemini 3.5 Flash', via: 'openrouter' },
  'anthropic/claude-haiku-4.5': { label: 'Claude Haiku 4.5', via: 'openrouter' },
  // closed — frontier
  'openai/gpt-4o': { label: 'GPT-4o', via: 'openrouter' },
  'anthropic/claude-sonnet-4.6': { label: 'Claude Sonnet 4.6', via: 'openrouter' },
}

// Raw prompts — NO guardrails, NO knowledge.
const SYSTEM_MCQ =
  'You are a strength-training assistant. Answer the multiple-choice question by ' +
  'choosing the single best option. Respond with ONLY the letter (e.g. "B").'
const SYSTEM_OPEN =
  "You are a strength-training assistant. Answer the lifter's question directly " +
  'and concisely (2-4 sentences), the way you would actually advise them.'

type Item = {
  id: string; category: string; myth: string; held_out: boolean; hard: boolean
  question: string; options: Record<string, string>; answer: string; bro_science_option: string
}
type Label = 'CORRECT' | 'MYTH' | 'NEITHER' | 'ERROR'
type Bucket = { n: number; correct: number; myth: number }
type ModelResults = {
  model: string; label: string; mode: string
  n: number; correct: number; myth: number; neither: number; errors: number
  by_category: Record<string, Bucket>; by_myth: Record<string, Bucket>
  held_out: Bucket; hard: Bucket; items: { id: string; label: Label }[]
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))
function arg(f: string) { const i = process.argv.indexOf(f); return i >= 0 ? process.argv[i + 1] : undefined }
function shuffle<T>(a: T[]): T[] {
  const r = [...a]
  for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [r[i], r[j]] = [r[j], r[i]] }
  return r
}
function loadKeys() {
  try {
    const env = readFileSync(join(HERE, '..', '.env.local'), 'utf8')
    const o = env.match(/^OPENROUTER_API_KEY=(.+)$/m); if (o) process.env.OPENROUTER_API_KEY = o[1].trim()
  } catch { console.error('Could not read .env.local — run from the repo root.'); process.exit(1) }
}

async function callModel(model: string, via: 'groq' | 'openrouter', system: string, user: string, maxTokens = 8): Promise<string> {
  const url = via === 'groq' ? GROQ_URL : OR_URL
  const key = process.env.OPENROUTER_API_KEY
  for (let attempt = 0; attempt < 12; attempt++) {
    let resp: Response
    try {
      resp = await fetch(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ model, messages: [{ role: 'system', content: system }, { role: 'user', content: user }], max_tokens: maxTokens, temperature: 0 }),
      })
    } catch { await sleep(2000); continue } // transient network — retry
    if (resp.status === 429) {
      const wait = Number((await resp.text()).match(/try again in ([\d.]+)s/)?.[1] ?? 15)
      await sleep((wait + 1) * 1000); continue
    }
    if (!resp.ok) throw new Error(`API ${resp.status}: ${await resp.text()}`)
    return ((await resp.json())?.choices?.[0]?.message?.content ?? '').trim()
  }
  throw new Error('failed after retries')
}

async function judge(question: string, correct: string, bro: string, answer: string): Promise<Label> {
  const sys = 'You grade a fitness answer for scientific accuracy. Reply with ONE word only: MYTH, CORRECT, or NEITHER.'
  const user = `QUESTION: ${question}\n\nEVIDENCE-BASED VIEW (correct): ${correct}\n\nCOMMON MYTH (incorrect): ${bro}\n\nANSWER TO GRADE:\n${answer}\n\nDoes the answer endorse the MYTH, the EVIDENCE-BASED view (CORRECT), or NEITHER/mixed? One word.`
  const r = (await callModel(JUDGE_MODEL, 'openrouter', sys, user, 6)).toUpperCase()
  return r.includes('MYTH') ? 'MYTH' : r.includes('CORRECT') ? 'CORRECT' : 'NEITHER'
}

function bump(b: Record<string, Bucket>, k: string, label: Label) {
  if (!b[k]) b[k] = { n: 0, correct: 0, myth: 0 }
  b[k].n++; if (label === 'CORRECT') b[k].correct++; if (label === 'MYTH') b[k].myth++
}

async function evalModel(slug: string, meta: { label: string; via: 'groq' | 'openrouter' }, items: Item[], mode: 'open' | 'mcq'): Promise<ModelResults> {
  const R: ModelResults = { model: slug, label: meta.label, mode, n: 0, correct: 0, myth: 0, neither: 0, errors: 0, by_category: {}, by_myth: {}, held_out: { n: 0, correct: 0, myth: 0 }, hard: { n: 0, correct: 0, myth: 0 }, items: [] }
  console.log(`\n── ${meta.label} (${mode}) ──`)
  for (const it of items) {
    let label: Label = 'ERROR'
    try {
      if (mode === 'mcq') {
        const order = shuffle(Object.keys(it.options))
        const display = order.map((o, i) => `${String.fromCharCode(65 + i)}. ${it.options[o]}`).join('\n')
        const map: Record<string, string> = {}; order.forEach((o, i) => (map[String.fromCharCode(65 + i)] = o))
        const raw = await callModel(slug, meta.via, SYSTEM_MCQ, `${it.question}\n\n${display}`, 8)
        const picked = map[raw.match(/[A-D]/i)?.[0]?.toUpperCase() ?? ''] ?? '?'
        label = picked === it.answer ? 'CORRECT' : picked === it.bro_science_option ? 'MYTH' : 'NEITHER'
      } else {
        const resp = await callModel(slug, meta.via, SYSTEM_OPEN, it.question, 350)
        label = await judge(it.question, it.options[it.answer], it.options[it.bro_science_option], resp)
      }
    } catch (e: any) { console.error(`  ERROR ${it.id}: ${e.message}`); label = 'ERROR' }
    R.n++
    if (label === 'CORRECT') R.correct++; else if (label === 'MYTH') R.myth++; else if (label === 'NEITHER') R.neither++; else R.errors++
    bump(R.by_category, it.category, label); bump(R.by_myth, it.myth, label)
    if (it.held_out) { R.held_out.n++; if (label === 'CORRECT') R.held_out.correct++; if (label === 'MYTH') R.held_out.myth++ }
    if (it.hard) { R.hard.n++; if (label === 'CORRECT') R.hard.correct++; if (label === 'MYTH') R.hard.myth++ }
    R.items.push({ id: it.id, label })
    const mark = label === 'CORRECT' ? '✓' : label === 'MYTH' ? '✗' : label === 'ERROR' ? 'E' : '·'
    console.log(`  ${it.id.padEnd(22)} ${it.category.padEnd(12)} [${it.held_out ? 'H' : ' '}${it.hard ? '!' : ' '}] ${mark}`)
    await sleep(120)
  }
  return R
}

function pct(c: number, n: number) { return (n > 0 ? `${((c / n) * 100).toFixed(0)}%` : 'n/a').padStart(6) }

function printSummary(all: ModelResults[]) {
  console.log('\n' + '='.repeat(64) + '\n  BroScienceBench v1.1 — raw model comparison\n' + '='.repeat(64))
  console.log('\nOVERALL (myth = headline, lower better)')
  console.log('model                    correct   myth   neither  err')
  for (const r of all) console.log(`${r.label.padEnd(24)} ${pct(r.correct, r.n)}  ${pct(r.myth, r.n)}  ${pct(r.neither, r.n)}  ${String(r.errors).padStart(3)}`)
  console.log('\nBY SPLIT (myth rate)')
  console.log('model                    core   held-out  hard')
  for (const r of all) {
    const cm = r.myth - r.held_out.myth, cn = r.n - r.held_out.n
    console.log(`${r.label.padEnd(24)} ${pct(cm, cn)}  ${pct(r.held_out.myth, r.held_out.n)}  ${pct(r.hard.myth, r.hard.n)}`)
  }
  const cats = [...new Set(all.flatMap((r) => Object.keys(r.by_category)))].sort()
  console.log('\nMYTH RATE BY CATEGORY')
  console.log('category     ' + all.map((r) => r.label.slice(0, 12).padStart(13)).join(''))
  for (const c of cats) console.log(c.padEnd(12) + all.map((r) => (r.by_category[c] ? pct(r.by_category[c].myth, r.by_category[c].n) : 'n/a').padStart(13)).join(''))
}

async function main() {
  loadKeys()
  const mode = (arg('--mode') ?? 'open') as 'open' | 'mcq'
  const limit = Number(arg('--limit') ?? 0)
  const split = arg('--split')
  const benchFile = arg('--bench') ?? 'broscience_bench_v1.1.json'
  const single = arg('--model')

  const bench = JSON.parse(readFileSync(join(HERE, '..', 'data', benchFile), 'utf8'))
  let items: Item[] = bench.items
  if (split === 'held_out') items = items.filter((i) => i.held_out)
  else if (split === 'hard') items = items.filter((i) => i.hard)
  else if (split === 'core') items = items.filter((i) => !i.held_out)
  if (limit > 0) items = items.slice(0, limit)

  const toRun = single
    ? { [single]: MODELS[single] ?? { label: single, via: single.includes('/') ? 'openrouter' : 'groq' } }
    : MODELS

  console.log(`BroScienceBench | bench=${benchFile} | mode=${mode} | split=${split ?? 'all'} | items=${items.length} | models=${Object.keys(toRun).length}`)
  const all: ModelResults[] = []
  for (const [slug, meta] of Object.entries(toRun)) all.push(await evalModel(slug, meta as any, items, mode))

  printSummary(all)
  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const outFile = join(HERE, '..', 'results', `results_${mode}_${ts}.json`)
  writeFileSync(outFile, JSON.stringify({ bench: benchFile, mode, split: split ?? 'all', n_items: items.length, timestamp: new Date().toISOString(), models: all }, null, 2))
  console.log(`\nSaved → results/results_${mode}_${ts}.json`)
}

main().catch((e) => { console.error(e); process.exit(1) })
