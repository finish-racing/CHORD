# CHORD Process Alignment Update v1

This update corrects the build and testing policy for CHORD.

## Correct policy

The CHORD build is now governed by the following rules:

1. **Build directly toward the final Ubuntu release app**
   - The only real target is the fully completed CHORD Ubuntu application.
   - The final installer, final app behavior, final documentation, and final debug support are the actual goal.

2. **Waves and chunks are internal construction boundaries only**
   - Waves exist only to keep the build process stable inside this chat environment.
   - Waves are checkpoints for saving progress and avoiding timeouts or environment loss.
   - Waves are not independent field-test milestones.

3. **Do not treat each wave as a separately tested Ubuntu release**
   - There is no requirement to install or test every wave independently on the Ubuntu laptop.
   - A wave may end in a saved codebase checkpoint rather than an installable release candidate.

4. **No intermediate testing in this environment counts as project testing**
   - Any compile checks, packaging checks, or structural validation done here are only internal sanity checks.
   - They do not replace real-world Ubuntu testing.

5. **Real testing happens only on the final app running on the Ubuntu laptop**
   - The actual test cycle for CHORD is the completed Ubuntu application installed and run on the user's laptop.
   - Debugging artifacts, logs, dumps, and state traces exist to support that final laptop-based testing cycle.

6. **Installer work should be aimed at the final release**
   - The installer, upgrade, rollback, and reset tooling do not need to be re-packaged for every wave.
   - They should be built as part of the direct march to the final release.

## Practical implications

- Release packages remain useful as implementation and tracking boundaries.
- They should no longer imply mandatory per-package Ubuntu installation.
- Tracker and control documents should use package completion as an internal progress measure, not a field-test gate.
- Wave A and later waves should be interpreted as saved progress toward the finished app.

## Documentation rule

If any existing CHORD document suggests that each wave/package must be Ubuntu-tested independently before moving on, this update supersedes that language.
