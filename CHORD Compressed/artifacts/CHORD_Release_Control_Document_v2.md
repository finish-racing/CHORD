# CHORD Release Control Document v2

## Current controlling baseline

- Product: **CHORD**
- Engine: **PRISM Engine**
- Current external handoff baseline: **CHORD / PRISM master handoff v10**
- Current implementation baseline: **CHORD Wave A v4 Lock**
- Current control state: **Release Package 1 is code-complete and frozen as the implementation baseline**
- Current process state: **Waves/packages are internal build checkpoints, not required Ubuntu test milestones**

## Control interpretation

### Release Package 1 / Wave A Lock
Wave A is now treated as:
- the current code baseline for future development,
- a frozen checkpoint for continuing work,
- not a requirement for a separate Ubuntu field test before Wave B begins.

### Release Packages 2–13
These remain the required build packages toward the final CHORD release, but their completion is measured as:
- scoped code completion,
- scoped documentation completion,
- scoped checkpoint completion.

They are not individually required to become laptop-tested release candidates.

## Final external test gate

The only external test gate that matters for project acceptance is:

**The fully completed CHORD Ubuntu app installed and running on the user's laptop.**

All intermediate build activity should be optimized toward reaching that final gate efficiently and safely.
