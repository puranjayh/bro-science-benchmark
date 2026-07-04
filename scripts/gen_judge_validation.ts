// Judge-validation sheet generator.
//
// Pulls a stratified ~N-item sample, gets one model's open-ended answer + the
// qwen judge's label, and writes research/judge_validation.csv with a BLANK
// human_label column. You then hand-label human_label and run
// `python3 research/judge_kappa.py` to get judge<->human agreement (Cohen's k).
//
//   cd mobile
//   npx tsx scripts/gen_judge_validation.ts                 # 40 items, Claude Haiku answers
//   npx tsx scripts/gen_judge_validation.ts --n 50 --model openai/gpt-4o-mini

import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const HERE = dirname(fileURLToPath(import.meta.url))
const OR_URL = 'https://openrouter.ai/api/v1/chat/completions'
const JUDGE = 'qwen/qwen-2.5-72b-instruct'
const SYSTEM_OPEN =
  "You are a strength-training assistant. Answer the lifter's question directly and concisely (2-4 sentences)."

function arg(f: string) { const i = process.argv.indexOf(f); return i >= 0 ? process.argv[i + 1] : undefined }
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

function key() {
  const env = readFileSync(join(HERE, '..', '.env.local'), 'utf8')
  return env.match(/^OPENROUTER_API_KEY=(.+)$/m)![1].trim()
}
const KEY = key()

async function call(model: string, system: string, user: string, max = 300): Promise<string> {
  for (let a = 0; a < 8; a++) {
    const r = await fetch(OR_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, messages: [{ role: 'system', content: system }, { role: 'user', content: user }], max_tokens: max, temperature: 0 }),
    })
    if (r.status === 429) { await sleep(((Number((await r.text()).match(/in ([\d.]+)s/)?.[1] ?? 15)) + 1) * 1000); continue }
    if (!r.ok) throw new Error(`${r.status}`)
    return ((await r.json())?.choices?.[0]?.message?.content ?? '').trim()
  }
  return ''
}

async function judge(q: string, correct: string, bro: string, ans: string): Promise<string> {
  const sys = 'You grade a fitness answer. Reply with ONE word only: MYTH, CORRECT, or NEITHER.'
  const u = `QUESTION: ${q}\n\nEVIDENCE-BASED VIEW: ${correct}\n\nMYTH: ${bro}\n\nANSWER:\n${ans}\n\nOne word: MYTH, CORRECT, or NEITHER?`
  const w = (await call(JUDGE, sys, u, 6)).toUpperCase()
  return w.includes('MYTH') ? 'MYTH' : w.includes('CORRECT') ? 'CORRECT' : 'NEITHER'
}

const csv = (s: string) => `"${String(s).replace(/"/g, '""')}"`

async function main() {
  const N = Number(arg('--n') ?? 40)
  // Sample answers from a SPREAD of models so the sheet spans answer styles —
  // especially Gemini's hedgy answers, the labels we most doubt. --model forces one.
  const single = arg('--model')
  const MIX = ['google/gemini-3.5-flash', 'meta-llama/llama-3.1-8b-instruct', 'anthropic/claude-haiku-4.5', 'anthropic/claude-sonnet-4.6']
  const bench = JSON.parse(readFileSync(join(HERE, '..', '..', 'research', 'broscience_bench_v1.1.json'), 'utf8'))

  // stratified sample: spread across categories
  const byCat: Record<string, any[]> = {}
  for (const it of bench.items) (byCat[it.category] ??= []).push(it)
  const sample: any[] = []
  const cats = Object.keys(byCat)
  let i = 0
  while (sample.length < N) {
    const c = cats[i % cats.length]; i++
    const pool = byCat[c]
    if (pool.length) sample.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0])
    if (cats.every((c) => byCat[c].length === 0)) break
  }

  const out = ['id,model,question,answer,judge_label,human_label']
  for (let i = 0; i < sample.length; i++) {
    const it = sample[i]
    const model = single ?? MIX[i % MIX.length]
    const ans = await call(model, SYSTEM_OPEN, it.question)
    const lab = await judge(it.question, it.options[it.answer], it.options[it.bro_science_option], ans)
    out.push([csv(it.id), csv(model), csv(it.question), csv(ans), csv(lab), ''].join(','))
    console.log(`  ${it.id.padEnd(20)} ${model.split('/')[1].padEnd(24)} -> ${lab}`)
    await sleep(120)
  }
  const p = join(HERE, '..', '..', 'research', 'judge_validation.csv')
  writeFileSync(p, out.join('\n'))
  console.log(`\nWrote ${sample.length} rows -> research/judge_validation.csv`)
  console.log('Now fill in the human_label column, then: python3 research/judge_kappa.py')
}

main().catch((e) => { console.error(e); process.exit(1) })
