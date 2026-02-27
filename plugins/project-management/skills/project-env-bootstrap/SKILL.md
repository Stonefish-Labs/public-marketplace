---
name: project-env-bootstrap
description: >
  Scaffold the PM system directory structure from scratch. Creates the lifecycle
  folders (Proposed, On-Deck, Active, Paused, Archive, Groups) needed for project
  management. Use when setting up a fresh workspace, initializing the PM system for
  the first time, the user says "bootstrap", "set up my PM system", "create the
  folder structure", or uses /bootstrap. Safe to run repeatedly -- skips folders
  that already exist.
---

# Bootstrap

Sets up the root directory structure for the PM system.

## Steps

1. Run the bootstrap script (path relative to this skill):

   ```
   python scripts/bootstrap.py
   ```

2. Report the output to the user -- which folders were created and which were skipped.
