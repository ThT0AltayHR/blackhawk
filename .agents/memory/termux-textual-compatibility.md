---
name: Termux and Textual compatibility
description: Compatibility rules for terminal-first Python tools in this workspace
---

Termux-first Python tools should default to a dependency-free ANSI interface and
only import richer terminal UI libraries lazily. Keep the richer UI stylesheet
to the common Textual rule subset; responsive stylesheet extensions can prevent
the entire app from starting on some Textual versions.

**Why:** The upstream BlackHawk UI failed before rendering because its stylesheet
used responsive rules unsupported by the installed Textual parser. A mandatory
startup token gate also made non-interactive and mobile launches brittle.

**How to apply:** Make `--ui ansi` and automatic Termux detection reliable, keep
startup free of credential prompts, and treat optional UI dependencies as a
fallback enhancement rather than a launch requirement.