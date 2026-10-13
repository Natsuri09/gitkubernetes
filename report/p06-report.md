# CTE412 Practical 6 — Report

**Student number:** 02230137  **Name:** REPLACE WITH YOUR FULL NAME

> Fill every `…` from YOUR OWN measurements in `evidence/`. Delete the italic
> prompts when you have written the section.

## 1. Objective

*Two or three sentences in your own words: what problem the practical addresses
(releases that take the service offline, unmeasured), what you built to measure
it, and which three strategies you compared.*

## 2. Environment

| Item | Value |
| --- | --- |
| Operating system | … |
| Docker | … (`docker version`) |
| kind | v0.33.0 (`kind version`) |
| kubectl (client) | … (`kubectl version`) |
| Kubernetes (cluster) | … (`kubectl version`, Server Version) |
| Application language | Python 3.13, standard library only |
| Base image | `python:3.13-alpine` (monitor: `busybox:1.37`) |

## 3. Results

Take *requests observed* and *failed requests* from the `summarise.sh` output,
the *mixed-version window* from its last line, and the *peak number of
notice-board Pods* from your Pod watches. Window is in seconds (timestamps have
one-second resolution).

| Release | Requests observed | Failed requests | Mixed-version window (s) | Peak notice-board Pods | Evidence |
| --- | --- | --- | --- | --- | --- |
| Recreate (1.0.0 → 1.1.0) | … | … | … | … | `t5-recreate-summary.txt` |
| RollingUpdate (1.0.0 → 1.1.0) | … | … | … | … | `t5-rolling-summary.txt` |
| Broken release (1.2.0-broken) | … | … | n/a | … | `t6-summary.txt` |
| Blue/green switch 1 (blue → green) | … | … | … | … | `t7-switch1-summary.txt` |
| Blue/green switch 2 (green → blue) | … | … | … | … | `t7-switch2-summary.txt` |
| Blue/green switch 3 (blue → green) | … | … | … | … | `t7-switch3-summary.txt` |
| Flag change (rolling restart of green) | … | … | … | … | `t8-summary.txt` |

## 4. Analysis

### A1. Strategies ranked by failed requests

*Rank them. For each, explain from your logs the mechanism that produced the
number: which Pods existed, when the EndpointSlice was empty or not, what the
monitor line looked like. Cite `t5-recreate-monitor-log.txt`,
`t5-rolling-monitor-log.txt`, `t7-monitor-switches.txt`, `t5-rolling-pod-watch.txt`.*

### A2. Why the broken release did or did not cause failed requests

*Name the specific fields in `manifests/rolling/deployment.yaml` (readiness
probe, `maxUnavailable`, `maxSurge`, `progressDeadlineSeconds`,
`minReadySeconds`, liveness probe path). Then, for each field, predict what the
monitor would have recorded had it been left at its default value. Cite
`t6-conditions.txt`, `t6-pods-during-failure.txt`, `t6-summary.txt`.*

### A3. RollingUpdate versus blue/green

| Axis | RollingUpdate | Blue/green |
| --- | --- | --- |
| Mixed-version window | … s | … s |
| Peak resource use against quota (`requests.cpu`, Pods) | … | … (`t7-quota-used.txt`) |
| Time taken to roll back | … | … |

*Add two or three sentences interpreting the table.*

### A4. A situation where Recreate is the correct choice

*One realistic situation (for example, two versions must never run at the same
time) and why the measured downtime is acceptable there.*

### A5. What the feature flag allowed, and what it did not avoid

*What changed without building a new image; what still had to happen (see
`t8-running-pods-flag.txt`) and why.*

## 5. Reflection

**An error I met.** *The command, the output that revealed the problem (quote
it), and the reasoning that resolved it.*

**Something that remains unclear.** *…*

## 6. References

*Only documentation you actually consulted, with date of access, e.g.
Kubernetes documentation — Deployments, accessed 2026-10-DD.*
