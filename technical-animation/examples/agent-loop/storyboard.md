# Storyboard / 600 frames

| Time | Technical change | Visual action | Why it moves |
|---|---|---|---|
| 0.00–1.35 | Goal supplied | Task ticket enters; robot settles and looks at the tool | Establish an objective before execution |
| 1.35–2.70 | First test call, then execution | Arm anticipates; TEST follows upper path; machine activates only on arrival | Separate choosing an action from doing it |
| 2.70–3.50 | Failure returned | Red FAIL receipt; return packet follows lower path | An external observation comes back, not an invented answer |
| 3.50–4.45 | Next decision uses the observation | Receipt enters context stack; head tilts; hand considers the sign error | Feedback changes the next action |
| 4.45–5.50 | Apply patch | Yellow PATCH moves outward; old/new code comparison; machine code updates on arrival | Concrete change, not vague self-improvement |
| 5.50–6.75 | Retest executes | Another TEST; execution indicator, then PASS | A modification is not automatically success |
| 6.75–8.00 | Success returned, goal checked | Green result returns, model receives it and settles | Success must be observed before completion |
| 8.00–10.00 | Stop | Task gets a tick; no new packets; full feedback loop held with takeaway | Explain the loop and its stopping boundary |

Runtime event detail lives in project.json. Camera/labels are secondary and never advance the technical state.
