---
name: gvim
description: Use when a path to a plaintext file shows up in the conversation.
---

Render the file path as a hyperlink that opens the plaintext file in gvim.

Use the `gvim://` scheme, not `file://`. It is handled by `~/.local/bin/gvim-url-handler`, which opens the file in gvim. Plain `file://` links open in the system default app instead. Use the absolute path and percent-encode spaces and other special characters:

[/home/kit/notes/my note.md](gvim:///home/kit/notes/my%20note.md)
