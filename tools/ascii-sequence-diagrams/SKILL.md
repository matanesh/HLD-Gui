---
name: ascii-sequence-diagrams
description: Create stable fixed-column ASCII sequence diagrams for legacy or closed-network Confluence pages that cannot render Mermaid, PlantUML, XML diagram formats, or modern diagram plugins. Use whenever technical documentation needs components, lifelines, directional arrows, request/response flows, or long message labels rendered as plain text without alignment drift.
---

# ASCII Sequence Diagrams

Generate sequence diagrams through `scripts/render_ascii_sequence.py`. Never draw or repair spacing manually.

## Mandatory workflow

1. Convert the requested interaction into a JSON specification.
2. Keep participant IDs short and unique. Keep participant labels and message labels in printable English ASCII.
3. Preserve the default `lane_width` of 40 unless the user explicitly requests a denser or wider diagram.
4. Run:

   ```bash
   python3 scripts/render_ascii_sequence.py diagram.json --markdown
   ```

5. Use the script output verbatim. Never hand-edit spaces, arrows, boxes, or lifelines after rendering.
6. If the content is wrong, change the JSON and rerun the script.
7. Treat a nonzero exit code as a failed diagram; fix the input instead of bypassing validation.
8. Put the result in a Confluence Code Block or Preformatted block. Never paste it into proportional-font body text.

## Input format

```json
{
  "participants": [
    {"id": "frontend", "label": "FRONTEND"},
    {"id": "backend", "label": "BACKEND / BFF"},
    {"id": "core", "label": "CORE SERVICE"}
  ],
  "settings": {
    "lane_width": 40,
    "box_inner_width": 18
  },
  "messages": [
    {
      "from": "frontend",
      "to": "backend",
      "label": "POST /api/login with username, password, device metadata and correlation ID"
    },
    {
      "from": "backend",
      "to": "core",
      "label": "Validate credentials and load the latest authorization policy"
    },
    {
      "from": "core",
      "to": "backend",
      "label": "Authentication approved; return user ID, roles and policy version"
    },
    {
      "from": "backend",
      "to": "frontend",
      "label": "200 OK with access token, refresh token and initial UI permissions"
    }
  ]
}
```

## Non-negotiable layout rules

- Do not use tabs.
- Do not use Unicode box-drawing characters.
- Do not use Hebrew or other right-to-left text inside the diagram. Put Hebrew explanations outside the code block.
- Do not calculate spacing by eye.
- Do not place a long label directly on an arrow and extend the line around it.
- Allow the renderer to wrap every label inside the fixed channel next to its source participant.
- Allow arrows to cross intermediate lifelines; the renderer restores every lifeline on the following row.
- Use identical participant spacing throughout one diagram.
- Split a very large flow into several diagrams when it has more than six participants or becomes difficult to read horizontally.

## Reliability contract

The renderer owns all column positions. Long labels may add rows but must never move a participant, lifeline, box edge, or arrow endpoint. Backward arrows, non-adjacent arrows, wrapped participant names, long unbroken tokens, and self-calls must be produced only by the renderer.

The guarantee applies when the final text is displayed in a monospaced, left-to-right Code Block and the script completes successfully.
