# v117 Tsubasa ConvNeXt No-Remap Plan

Created: 2026-05-19 06:49 UTC

## Trigger

v116 completed Run-mode and proved the CC0 Tsubasa ConvNeXt SED source is
CPU-runnable, but its train-window remap collapsed proxy macro to `0.85930903`.

## Change

v117 keeps the same source and clean notebook scaffold but disables output-column
remapping:

- `remap_cols = identity_cols`
- `remap_strength = 0`
- rank stabilizer reduced to a fixed light `0.08`

## Purpose

Isolate whether the raw same-index ConvNeXt SED signal is usable before
reintroducing any remap/trust mechanism. If v117 still collapses, the Tsubasa
ConvNeXt source should be rejected for this lane.

## Gate

Run-mode only. Reject if proxy remains far below v110/v114 or if runtime/schema
checks fail.
