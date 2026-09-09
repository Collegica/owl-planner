---
id: IDEA-0019
lens: canadian-planners
capability: statement-import
status: retired
effort: L
value: low
promoted_to: 
---

# A read-only open-banking importer — retired

Arrive Finance's architecture is account data arriving through a bank-aggregation API, with
the Consumer-Driven Banking Act's phase-one read access as the tailwind. It is the natural
next importer and it is retired here on purpose: the tool's premise is no credentials, no
network, files the person exported themselves — the thing Retire, Eh? also lists as out of
scope. An aggregator token in a config file breaks the promise that makes the tool acceptable.

Watched, not built. If a bank ever offers a signed, offline statement format, that is an
import; a live connection is not.
