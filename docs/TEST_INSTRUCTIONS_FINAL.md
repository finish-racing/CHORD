# CHORD Final Ubuntu Test Instructions

Use these only when the final Ubuntu package is ready to be tested on the laptop.

## Fresh install flow
1. install prerequisites / run installer
2. configure `/etc/chord/chord.env`
3. configure `/etc/chord/config.toml`
4. initialize database
5. start service
6. open web UI
7. create run
8. upload Top 25 + playlist set
9. complete quiz
10. run pipeline
11. inspect dashboard
12. export recommendations and curated playlist
13. if needed, collect diagnostics and debug artifacts

## What to verify
- service starts
- uploads import cleanly
- quiz saves
- pipeline progresses through each stage
- dashboard panels populate
- exports download
- debug mode creates expected artifacts when enabled
