# Prototype Notes

## Question

Can a loop-engineering workflow be made explicit enough that a human can see the goal, active task, verification gate, retry budget, and stop condition at every step?

## Current Verdict

Pending hands-on use.

## Interesting Things To Watch

- Does the task need a separate `needs_review` state, or is `in_progress + attempts > 0` enough?
- Is a retry budget per task enough, or should the whole loop also track token/cost budget?
- Should checker failure automatically restart the same task, or should it return to queue for prioritization?
- Which state should be durable in a real implementation: full transcript, compact notes, or only task status?

## Delete Or Absorb

If this feels right, absorb `loop_core.py` into a real runner and delete `loop_tui.py`.
