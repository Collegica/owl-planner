# Ideas

The stage before a proposal. A proposal asks for a decision; an idea asks for nothing. It is
cheap to write, allowed to be wrong, and allowed to die — as long as it says where it came from
and, when it moves, where it went. (Method: the LENS handbook.)

## One idea, one file

`docs/ideas/<YYYYMMDD>_<slug>.md`, starting with a YAML header:

```yaml
---
id: IDEA-0007
lens: data                 # where it came from — see "Lenses"
capability: <id>           # an id from docs/capabilities.yaml — the same ids as openspec/specs/
status: seed               # seed | explored | promoted | retired
effort: S                  # S days · M weeks · L a quarter, or a dependency we do not control
value: high                # high | medium | low — what it buys if it works
promoted_to:               # the proposal or plan, once status is promoted
---
```

then a title and as little prose as makes the idea legible: what we would do, what it would
buy, what it would cost, and the evidence or observation that produced it. A paragraph is
fine. A page is the upper bound — past that it is a proposal and should be written as one.

**Every idea names a capability.** The index groups by it, so a capability with no ideas is
visible, and an idea that fits none is itself worth noticing.

`effort` and `value` are the two judgements the index orders by ("In order": value first, then
effort). They are opinions, held in the header so they are reviewed with the idea.

## Lenses

A lens is a question that generates ideas, answered once and mined. Each lives in
`lenses/<slug>.md`; the ideas it yields are separate files that cite it.

Four lenses need no document:

| lens | what it means |
|---|---|
| `data` | a measurement that surprised us |
| `review` | a person judging the system's output, and what the wrong answers had in common |
| `incident` | something broke or misled, and the fix suggested a better shape |
| `customer` | something a user, operator or buyer said |

## Status

| status | meaning |
|---|---|
| `seed` | written down, not examined |
| `explored` | someone looked: sized it, found prior art, ran a measurement — and it survived |
| `promoted` | became a proposal or a plan; `promoted_to` says which |
| `retired` | dropped, with one line in the file saying why |

## The index is generated

`index.md` is written by `pixi run ideas-index` from the headers and must not be edited by
hand; `pixi run ideas-check` fails when it is stale or a header is malformed, and CI runs it. Its first section,
"In order", is the answer to "which idea next".

## Where ideas go when they grow up

An idea that is worth a decision becomes an OpenSpec change: `pixi run propose <name>`, then
set the idea's `status: promoted` and `promoted_to: openspec/changes/<name>`. The idea file
stops being edited; the change is now the record.
