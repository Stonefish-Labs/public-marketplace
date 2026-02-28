#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic>=2.12.0",
# ]
# ///
"""
Doom Map IR Validator.

Usage:
  uv run validate.py <ir.json>
  uv run validate.py --schema
"""
import argparse
import json
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class RoomType(str, Enum):
    SMALL_ROOM = "small_room"
    MEDIUM_ROOM = "medium_room"
    LARGE_ROOM = "large_room"
    ARENA = "arena"
    SMALL_L = "small_l"
    MEDIUM_L = "medium_l"
    LARGE_L = "large_l"
    SMALL_OCTAGON = "small_octagon"
    MEDIUM_OCTAGON = "medium_octagon"
    LARGE_OCTAGON = "large_octagon"
    SMALL_OUTDOOR = "small_outdoor"
    LARGE_OUTDOOR = "large_outdoor"


class ThingPlacement(BaseModel):
    type: str
    count: int = Field(default=1, ge=1, le=50)
    x_offset: Optional[float] = None
    y_offset: Optional[float] = None


class RoomDefinition(BaseModel):
    id: str
    template: RoomType = RoomType.MEDIUM_ROOM
    floor_height: int = 0
    ceiling_height: int = 128
    light_level: int = Field(default=160, ge=0, le=255)
    things: list[ThingPlacement] = []
    is_secret: bool = False


class Connection(BaseModel):
    from_room: str
    to_room: str
    width: int = Field(default=64, ge=32, le=256)
    is_door: bool = False
    is_secret: bool = False


class MapIR(BaseModel):
    name: str = "MAP01"
    title: Optional[str] = None
    author: str = "AI Doom Generator"
    rooms: list[RoomDefinition]
    connections: list[Connection] = []

    def validate_connections(self) -> list[str]:
        room_ids = {r.id for r in self.rooms}
        errors = []
        for conn in self.connections:
            if conn.from_room not in room_ids:
                errors.append(f"Unknown room: {conn.from_room}")
            if conn.to_room not in room_ids:
                errors.append(f"Unknown room: {conn.to_room}")
        return errors


VALID_THINGS = {
    "player_start", "player_2_start", "player_3_start", "player_4_start", "deathmatch_start",
    "zombieman", "shotgun_guy", "imp", "demon", "spectre", "lost_soul",
    "cacodemon", "baron", "hell_knight", "arachnotron", "pain_elemental",
    "revenant", "mancubus", "arch_vile", "spider_mastermind", "cyberdemon",
    "stimpack", "medikit", "green_armor", "blue_armor", "soul_sphere", "megasphere",
    "clip", "shells", "rocket", "cell", "box_of_shells", "box_of_rockets", "cell_pack", "bullets",
    "shotgun", "super_shotgun", "chaingun", "rocket_launcher", "plasma_rifle", "bfg", "chainsaw",
    "blue_key", "red_key", "yellow_key", "blue_skull", "red_skull", "yellow_skull",
    "barrel", "pillar", "candelabra",
}


def validate_things(ir: MapIR) -> list[str]:
    errors = []
    for room in ir.rooms:
        for thing in room.things:
            if thing.type not in VALID_THINGS:
                try:
                    int(thing.type)
                except ValueError:
                    errors.append(f"Room '{room.id}': unknown thing type '{thing.type}'")
    return errors


def validate_player_start(ir: MapIR) -> list[str]:
    errors = []
    has_start = False
    for room in ir.rooms:
        for thing in room.things:
            if thing.type == "player_start":
                if has_start:
                    errors.append("Multiple player_start found (should be exactly one)")
                has_start = True
    if not has_start:
        errors.append("No player_start found (required)")
    return errors


def main():
    p = argparse.ArgumentParser(description="Validate Doom map IR")
    p.add_argument("input", nargs="?", help="IR JSON file to validate")
    p.add_argument("--schema", action="store_true", help="Print JSON schema")
    args = p.parse_args()

    if args.schema:
        print(json.dumps(MapIR.model_json_schema(), indent=2))
        return

    if not args.input:
        p.error("input file required (or use --schema)")

    try:
        data = json.loads(Path(args.input).read_text())
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        ir = MapIR.model_validate(data)
    except Exception as e:
        print(f"Schema validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    errors = []
    errors.extend(ir.validate_connections())
    errors.extend(validate_things(ir))
    errors.extend(validate_player_start(ir))

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"Valid: {len(ir.rooms)} rooms, {len(ir.connections)} connections")
    thing_count = sum(len(r.things) for r in ir.rooms)
    print(f"         {thing_count} thing placements")


if __name__ == "__main__":
    main()
