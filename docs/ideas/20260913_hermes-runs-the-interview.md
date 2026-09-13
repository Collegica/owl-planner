---
id: IDEA-0032
lens: review
capability: onboarding
status: explored
effort: S
value: high
promoted_to:
---

# Hermes runs the ask-your-AI loop, with the user answering

`ask-your-ai.md` was designed to be pasted into an AI chat; the answer comes
back by hand as `--merge answer.yml`. An agent that can run the tool, read the
pack, ask the user and merge the answer closes that loop without the paste —
and with the user still the one deciding, because the agent's instruction is
to ask, not to guess. Hermes Agent has a `clarify` tool that asks a batch of
questions with pickable choices, which is the interview's exact shape.

What it buys: the first run on a fresh clone stops at a question list the
user answers in a chat window, not a CSV they triage in a spreadsheet; the
same skill works in the terminal, in Hermes Desktop, and — if the user wants
— from a phone through Hermes's gateway. What it costs: a skill file and a
paragraph of README; no change to the engine.

What it does not change: the engine still makes no network request and
needs no key. The agent is the user's, chosen and paid for by them, and the
only thing it reads about their money is the pack that already carries none.
The model is the user's decision too — a cloud model sees merchant names, a
local one sees nothing that leaves the machine — and the README says so in
those words.

Related: IDEA-0007 (promoted to `first-run-interview`) puts the interview in
the engine on stdin; this puts it in an agent on top of the existing pack. They
are not in conflict — the agent would run either.

Explored 2026-09-13: `skills/owl-interview/SKILL.md`, `AGENTS.md`, the README
section, and a run on the invented household under an isolated Hermes profile.
