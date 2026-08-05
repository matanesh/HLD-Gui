#!/usr/bin/env python3
"""Render stable, fixed-column ASCII sequence diagrams from JSON."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Participant:
    id: str
    label: str


class DiagramError(ValueError):
    pass


def require_ascii(value: str, field: str) -> None:
    if not value.isascii() or any(ord(ch) < 32 for ch in value):
        raise DiagramError(
            f"{field} must contain printable ASCII only. "
            "Use English labels to avoid RTL and variable-width rendering errors."
        )


def wrapped(value: str, width: int) -> list[str]:
    parts = textwrap.wrap(
        " ".join(value.split()),
        width=width,
        break_long_words=True,
        break_on_hyphens=False,
    )
    return parts or [""]


class SequenceRenderer:
    def __init__(self, spec: dict[str, Any]) -> None:
        raw_participants = spec.get("participants")
        if not isinstance(raw_participants, list) or len(raw_participants) < 2:
            raise DiagramError("participants must be a list containing at least two items")

        participants: list[Participant] = []
        for index, item in enumerate(raw_participants):
            if isinstance(item, str):
                participant = Participant(item, item)
            elif isinstance(item, dict):
                participant = Participant(str(item.get("id", "")), str(item.get("label", "")))
            else:
                raise DiagramError(f"participants[{index}] must be a string or object")
            if not participant.id or not participant.label:
                raise DiagramError(f"participants[{index}] requires non-empty id and label")
            require_ascii(participant.id, f"participants[{index}].id")
            require_ascii(participant.label, f"participants[{index}].label")
            participants.append(participant)

        ids = [participant.id for participant in participants]
        if len(set(ids)) != len(ids):
            raise DiagramError("participant ids must be unique")

        settings = spec.get("settings", {})
        if not isinstance(settings, dict):
            raise DiagramError("settings must be an object")

        self.participants = participants
        self.messages = spec.get("messages", [])
        if not isinstance(self.messages, list):
            raise DiagramError("messages must be a list")

        self.box_inner = int(settings.get("box_inner_width", 18))
        self.lane_width = int(settings.get("lane_width", 40))
        self.margin = int(settings.get("margin", 2))
        if self.box_inner < 8:
            raise DiagramError("box_inner_width must be at least 8")
        self.box_width = self.box_inner + 2
        if self.lane_width < self.box_width + 4:
            raise DiagramError("lane_width must be at least box_inner_width + 6")
        if self.margin < 0:
            raise DiagramError("margin cannot be negative")

        first_center = self.margin + self.box_width // 2
        self.centers = [first_center + i * self.lane_width for i in range(len(participants))]
        self.width = self.centers[-1] + self.box_width // 2 + self.margin + 1
        self.by_id = {participant.id: i for i, participant in enumerate(participants)}
        self.rows: list[str] = []

    def new_row(self, lifelines: bool = False) -> list[str]:
        row = [" "] * self.width
        if lifelines:
            for center in self.centers:
                row[center] = "|"
        return row

    def append(self, row: list[str]) -> None:
        if len(row) != self.width:
            raise AssertionError("internal renderer error: invalid row width")
        self.rows.append("".join(row).rstrip())

    def append_lifelines(self) -> None:
        self.append(self.new_row(lifelines=True))

    def draw_participants(self) -> None:
        label_lines = [wrapped(participant.label, self.box_inner) for participant in self.participants]
        height = max(len(lines) for lines in label_lines)

        top = self.new_row()
        for center in self.centers:
            start = center - self.box_width // 2
            top[start : start + self.box_width] = "+" + "-" * self.box_inner + "+"
        self.append(top)

        for line_index in range(height):
            row = self.new_row()
            for center, lines in zip(self.centers, label_lines):
                start = center - self.box_width // 2
                text = lines[line_index] if line_index < len(lines) else ""
                row[start : start + self.box_width] = "|" + text.center(self.box_inner) + "|"
            self.append(row)

        bottom = self.new_row()
        for center in self.centers:
            start = center - self.box_width // 2
            bottom[start : start + self.box_width] = "+" + "-" * self.box_inner + "+"
        self.append(bottom)

    def indices_for(self, message: dict[str, Any], index: int) -> tuple[int, int]:
        source = str(message.get("from", ""))
        target = str(message.get("to", ""))
        if source not in self.by_id:
            raise DiagramError(f"messages[{index}].from references unknown participant {source!r}")
        if target not in self.by_id:
            raise DiagramError(f"messages[{index}].to references unknown participant {target!r}")
        return self.by_id[source], self.by_id[target]

    def draw_label(self, source: int, target: int, label: str) -> None:
        require_ascii(label, "message label")
        if source == target:
            neighbor = source + 1 if source < len(self.centers) - 1 else source - 1
        else:
            neighbor = source + (1 if target > source else -1)

        left, right = sorted((self.centers[source], self.centers[neighbor]))
        available = right - left - 4
        if available < 1:
            raise AssertionError("internal renderer error: message channel is too narrow")

        for part in wrapped(label, available):
            row = self.new_row(lifelines=True)
            row[left + 2 : right - 2] = part.center(available)
            self.append(row)

    def draw_arrow(self, source: int, target: int) -> None:
        if source == target:
            self.draw_self_arrow(source)
            return

        row = self.new_row(lifelines=True)
        source_x = self.centers[source]
        target_x = self.centers[target]
        left, right = sorted((source_x, target_x))
        for column in range(left + 1, right):
            row[column] = "-"
        row[source_x] = "|"
        row[target_x] = ">" if source_x < target_x else "<"
        self.append(row)

    def draw_self_arrow(self, source: int) -> None:
        center = self.centers[source]
        direction = 1 if source < len(self.centers) - 1 else -1
        end = center + direction * 6

        first = self.new_row(lifelines=True)
        for column in range(min(center, end) + 1, max(center, end)):
            first[column] = "-"
        first[center] = "|"
        first[end] = "+"
        self.append(first)

        middle = self.new_row(lifelines=True)
        middle[end] = "|"
        self.append(middle)

        last = self.new_row(lifelines=True)
        for column in range(min(center, end) + 1, max(center, end)):
            last[column] = "-"
        last[center] = "<" if direction > 0 else ">"
        last[end] = "+"
        self.append(last)

    def render(self) -> str:
        self.draw_participants()
        self.append_lifelines()

        for index, raw_message in enumerate(self.messages):
            if not isinstance(raw_message, dict):
                raise DiagramError(f"messages[{index}] must be an object")
            source, target = self.indices_for(raw_message, index)
            label = str(raw_message.get("label", "")).strip()
            if not label:
                raise DiagramError(f"messages[{index}].label must not be empty")
            self.draw_label(source, target, label)
            self.draw_arrow(source, target)
            self.append_lifelines()

        self.validate()
        return "\n".join(self.rows)

    def validate(self) -> None:
        if any(len(row) > self.width for row in self.rows):
            raise AssertionError("internal renderer error: a row exceeded the fixed diagram width")
        if "\t" in "\n".join(self.rows):
            raise AssertionError("internal renderer error: tab characters are forbidden")
        if not "\n".join(self.rows).isascii():
            raise AssertionError("internal renderer error: output must be ASCII")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON diagram specification")
    parser.add_argument("--markdown", action="store_true", help="wrap output in a fenced text block")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        spec = json.loads(args.input.read_text(encoding="utf-8"))
        diagram = SequenceRenderer(spec).render()
    except (OSError, json.JSONDecodeError, DiagramError, AssertionError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.markdown:
        print("```text")
        print(diagram)
        print("```")
    else:
        print(diagram)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
