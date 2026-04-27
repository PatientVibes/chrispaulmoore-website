# Agent harnesses are a commitment curve, not a checklist

Somewhere around last year it became normal to describe an agent by listing its parts. Orchestration loop, tools, memory, context management, prompt construction, output parsing, state, error handling, guardrails, verification, subagent orchestration, token tracking. Twelve of them. I've seen people compile similar lists on whiteboards, in LangChain tutorials, in architecture diagrams inside enterprises, and, most usefully for me, in Alex Ker's post ["Harnesses are everything. Here's how to optimize yours."](https://x.com/thealexker/status/2045203785304232162) That is the vocabulary I've been using as a working tool for the past several months.

This post is not a framework. It is what happened when I took Alex's taxonomy and tried to use it as a working tool against two different agents — one at work, one at home — and noticed where it held, where it bent, and where I still don't quite know what to do with it.

## The trap

The failure mode of any taxonomy is that readers treat it as a checklist. Twelve boxes. Tick them all. If your agent is missing verification loops, fix that. If you don't have subagent orchestration, add that. This reading produces agents that are over-engineered in one direction and strangely brittle in another — because what the taxonomy is is a vocabulary of surfaces on which agent behavior can be shaped. It does not tell you which surfaces to shape for the agent you are building. That part depends on the constraints you're operating under, and those are not in the list.

My claim, which I'll spend the rest of this post trying to earn: **components one through six are a foundation, components seven through twelve are a commitment curve, and which half of the curve you need is determined by the axioms of your deployment context, not by the taxonomy.**

## The list, briefly

In the order Alex presents them:

1. Orchestration loop
2. Tools
3. Memory
4. Context management
5. Prompt construction
6. Output parsing
7. State management
8. Error handling
9. Guardrails
10. Verification loops
11. Subagent orchestration
12. Token / cost tracking

Rather than restate each one, I'll lean on Alex's post for the definitions and spend my words on what I saw.

## Two agents, two axiom sets

The first agent is **chorus-agent**: a LangGraph ReAct agent running Qwen3-30B via the SS&C AI Gateway. Its job is narrow and high-stakes. Read AWD CSD binary forms, produce Chorus Classic XML, hold a structured `FormAnalysis` + `CrossFormReport` contract across multiple forms. The constraint set is not subtle. Multi-agent, regulated financial-services domain, a paid enterprise inference gateway, auditable output, and a hard distinction between Chorus system fields and client LOB fields that has to be preserved or the whole thing is useless. Errors are not tolerable. Hallucinated field names are not tolerable. A cross-form inconsistency that nobody catches is not tolerable. That's the constraint set.

The second agent is **kindle-pipeline**: a script-driven pipeline that pulls books, essays, and web articles from various sources (Marker-OCR'd books, web scrapes from Karakeep-bookmarked essays), produces a Kindle Scribe-targeted PDF with annotation margins plus an Obsidian markdown export, and runs an LLM proofreader over the OCR'd text to catch joined words, LaTeX artifacts, and other Marker-produced weirdness before it commits. It runs locally on Ollama against qwen3:8b on a laptop. Single user — me. No SLA. No compliance regime. No audit trail anyone will ever read. The constraint set is the inverse of chorus-agent. The cost of a bad run is that I reread a paragraph. That's the constraint set.

I have applied the same twelve-component taxonomy to both.

## Chorus-agent — where the full twelve were earned

The foundation (1–6) barely warrants discussion; every working agent has these in some form. The interesting question is the discretionary half.

For chorus-agent, the answer is the unsurprising one: all six earn their keep, and the reasons are specific. **State management** because gateway dropouts mid-cross-form would lose a day's work, and checkpointing at the per-form boundary maps onto the natural seams in the data. **Error handling** because three distinguishable failure modes (retry-worthy network blip, gateway reject, malformed model output) demand three different responses, and collapsing them into "retry harder" creates silent drift in regulated outputs. **Guardrails** because client-authored documents could carry instruction-shaped text, and the model must be unable to expand its narrow job — length caps, strict output schemas, a refusal to treat document content as instructions. **Subagent orchestration** because per-form analyses are independent and parallelizable while cross-form synthesis depends on them; the shape of the data demanded it.

Two of the six are worth a longer beat.

**Verification loops.** The cross-form report is a synthesis across independent per-form analyses. The synthesis is exactly the kind of step where LLMs are prone to confabulating consistency. A separate verification pass — check that each claim in the synthesis is grounded in at least one form-level analysis — catches the kind of failure a single-pass agent cannot catch in itself. This is not paranoia; it is a structural feature of how generation works. Verification is how you turn a text generator into a reporting system.

**Token / cost tracking.** The AI Gateway is paid. Usage is metered. A deployment without tracking is a deployment you cannot improve, because you cannot see what improvements cost. This one is obvious once you're writing checks.

Full stack, earned. Nothing in seven through twelve is there because the taxonomy said so. Each component is justified by a specific property of the constraint set.

## Kindle-pipeline — where the taxonomy bent

I also implemented all twelve for the kindle-pipeline. It is also documented as a 12/12 harness in the repo. Both of those things are true. Also true: several of the components are honestly overkill for the actual constraints, and the most important design decisions in the pipeline aren't well-described by the taxonomy at all.

**State management, honestly rethought.** The pipeline checkpoints per chunk and supports `--resume`. I have used that exactly twice, both times because I killed it for an unrelated reason. There is no SLA, no scale problem, no external interruption I need to survive — just me, one pipeline, occasionally ten books in a queue. Writing the checkpointing was a weekend of careful work; the value it has returned is the ability to kill and resume, which I could also have gotten from making chunks smaller and re-running. I don't regret having it, but I cannot, in honesty, defend it as necessary. It's there because the taxonomy implied I needed it, not because the constraint set demanded it.

**Verification loops.** The proofreader is followed by a separate verifier agent that reviews each proposed fix before it's applied. This sounds rigorous, and it is the pattern you'd reach for if the stakes were real. In practice, the *deterministic pre-pass* upstream of the proofreader does most of the useful work, and the persistent `proofreader_memory.json` of known false positives does most of the rest. The verifier agent, as an independent LLM call, catches real mistakes perhaps once every several chunks. Is that worth its latency and model time? Probably not, against the actual cost of a missed proofread in a personal book I am reading for pleasure on a Kindle. The verification loop is in the pipeline because it's good engineering practice. If I were being ruthless about matching the harness to the constraint set, I'd remove it and accept a slightly noisier read-through.

**Subagent orchestration.** The proofreader / verifier pair is a dual-agent pattern, which checks the subagent-orchestration box. I could almost certainly get 90% of the quality from a single, better-prompted agent with an explicit two-step rubric inside its own prompt — no second model call. The dual-agent structure is more ceremonial than load-bearing here.

Three components over-engineered against the real axioms. And yet, interestingly, the design decisions that *matter most* in the pipeline are not the ones the twelve-component taxonomy calls out.

**Deterministic pre-pass before the LLM.** `clean_markdown.py` runs a regex-driven analysis for joined words, duplicate headings, malformed LaTeX, and empty figure placeholders *before* the LLM is ever called. The LLM only sees chunks with surfaced issues, and its prompt includes the pre-analysis hints. This is the single most important architectural decision in the pipeline, and it is, I think, not a component in the harness at all. It is a stance about when to reach for the model and when not to. It falls awkwardly between orchestration (1), prompt construction (5), and guardrails (9) without being fully described by any of them. Its relationship to the rest of the system is: the LLM is the most expensive, slowest, and least reliable component. Minimize its surface area and narrow its task before invoking it. That is an axiom of my deployment; it is not a component.

**Persistent false-positive memory.** `proofreader_memory.json` accumulates patterns that have been flagged in the past and confirmed as non-issues. Each new run starts knowing what it has previously learned not to worry about. This is nominally memory (component 3), but the *use case* — a personal training set of edge cases accumulated over runs across my own corpus — is not anticipated by a taxonomy written for general agent design. It's a specific answer to a specific question: how do you avoid being wrong about the same thing twice in a system with no test suite?

**Section-aware chunking at heading boundaries.** Instead of fixed token windows, the proofreader chunks at heading seams. This is nominally context management (component 4), but "chunk at heading boundaries" reflects a *domain assumption*: the documents are structured prose with hierarchical headings, and reasoning within a section is more coherent than reasoning across one. If the documents were email chains, or legal briefs, or forum posts, this decision would be wrong. It's a constraint-driven design choice dressed up as a context-management choice.

These three — pre-pass gating, persistent false-positive memory, section-aware chunking — are the parts of the kindle-pipeline I would recommend to someone else. None of them are well-described by the twelve components. All of them fall out of the constraints of the deployment.

This is the pattern I keep running into: the taxonomy gives me a vocabulary for the parts I have to implement, but the interesting design is always in the axioms that the taxonomy takes as given.

## The commitment curve

Here is the reframe I'd offer.

Components 1–6 are a floor. Any agent you'd call working has these in some form: it loops (1), it can call things (2), it remembers enough to finish the task (3), it doesn't exceed the model's context (4), it constructs its prompts deliberately (5), it parses outputs back into something usable (6). Without any of these the agent simply does not function.

Components 7–12 are a commitment curve. Each one is an *investment* that exchanges complexity for a property of the system — durability, safety, accountability, auditability, economy. The cost of those investments is real. The value of them is context-dependent. Which of them you should make is determined by the axiom set of your deployment.

- **State management (7)** earns itself when the cost of a failed mid-run is higher than the cost of the checkpointing.
- **Error handling beyond retry-with-backoff (8)** earns itself when you have multiple distinguishable failure modes that demand different responses.
- **Guardrails (9)** earn themselves when untrusted content can reach the model's instruction surface.
- **Verification loops (10)** earn themselves when single-pass generation produces a kind of failure that single-pass generation cannot detect.
- **Subagent orchestration (11)** earns itself when the shape of the work is parallel, or when truly independent roles clarify the design.
- **Token/cost tracking (12)** earns itself when you are paying for usage, or when scale will eventually make you pay.

The question isn't "do I have all twelve." The question is which of seven through twelve the constraints of my deployment actually earn. For chorus-agent, the answer was all of them, and the reasons were specific. For kindle-pipeline, if I were being honest about the constraints, the answer is probably somewhere around eight or nine — the checkpointing, the dual-agent verifier, and the full subagent pattern are there more from good-hygiene instincts than from demand.

Neither of those answers is wrong. What's wrong is reading the list as a checklist and then quietly becoming over-engineered against imagined stakes — or under-engineered against real ones.

## A harder question I'm dodging

I've been writing as though seven through twelve are six independent dials. They aren't, quite. Verification loops imply state. Subagent orchestration implies error handling. Guardrails and verification both depend on output parsing being strict enough to police. The "curve" may not be one-dimensional — there's probably an ordering, where investing in one component changes which of the others come due. I don't have a defensible model of that ordering yet, and trying to argue one would be a different essay. Naming it as a thread I'm leaving unpulled feels more honest than pretending the six are independent.

## The one rule I can't yet place

Twelve, token and cost tracking, is where my commitment-curve reasoning breaks down in a way I want to note rather than resolve.

My honest position is that you should track tokens and cost on every project you build, because tracking is how you measure improvement, and measurement is how you learn. If you don't know what a behavior costs, you can't choose to change it. That is a hygiene rule, not a constraint-driven rule. It's closer to "always have tests" or "always commit small" — defensible in general, hard to defend in any specific case where the stakes make it clearly unnecessary.

Kindle-pipeline is the clearly-unnecessary case. It's fully local. Ollama runs on hardware I already own. There is no cost signal. There is no scale problem. There is no SLA or budget. And I still track tokens on it, because I can't quite bring myself to turn the habit off.

So is token tracking a floor component (1–6) disguised as a commitment curve component (7–12)? Is it a genuine hygiene rule that stands outside the constraint-driven logic? Or is it an instinct of mine that is strictly unjustified in the local case and I should just admit that?

I don't know. That's the interesting place to end, because it's the spot where my own argument doesn't quite close.

## What this is not

This is not a claim that Alex's taxonomy is wrong. It isn't. It's the most useful decomposition of agent internals I've come across, and most of what I've described above — the commitment curve framing, the constraint-axiom mapping — is a *reading* of the taxonomy, not a replacement for it.

It's also not a claim that I have a better framework. I don't. I have two agents I've built and a habit of asking, when I add a component, *what specifically about my deployment earns this*. If I had to name the contribution, it would be: the taxonomy is a vocabulary for the parts, but the interesting work is always in the axioms that determine which parts you need and how they should behave.

That much I can defend. The rest is noticing.

---

*Chris Moore. Citation: Alex Ker, ["Harnesses are everything. Here's how to optimize yours."](https://x.com/thealexker/status/2045203785304232162) Companion piece: [A reading pipeline I didn't design — I derived](/essays/karakeep-kindle-pipeline.html).*
