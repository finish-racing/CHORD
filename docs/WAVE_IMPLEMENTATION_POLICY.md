# Wave Implementation Policy

CHORD is built in release packages. Each package is real product code.

## Rules
- No demo-only code
- No fake UI shells
- No placeholder business logic presented as complete
- Every release package must leave behind usable production code
- Debug mode, validation, error handling, and documentation are required from the start

## Error handling levels
1. Standard mode
   - operator-safe messages
   - structured logging
   - normal failure behavior

2. Debug mode
   - expanded logging
   - artifact dumps
   - stack traces preserved in logs
   - state snapshots where practical

## Upgrade / rollback principle
Application code, database, config, and runtime artifacts are separate layers.
Later installer work must preserve:
- PostgreSQL data
- config files
- uploads
- cache
- exports
- logs/debug artifacts
