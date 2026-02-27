#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic>=2.12.0",
# ]
# ///
"""
Doom Map Generator - IR to WAD compiler.

Usage:
  uv run generate.py demo -o output.wad
  uv run generate.py from-ir map.json -o output.wad
  uv run generate.py schema
"""
import argparse
import json
import math
import random
import struct
import sys
from dataclasses import dataclass
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


THING_NAMES = {
    "player_start": 1, "player_2_start": 2, "player_3_start": 3,
    "player_4_start": 4, "deathmatch_start": 11,
    "zombieman": 3004, "shotgun_guy": 9, "imp": 3001,
    "demon": 3002, "spectre": 58, "lost_soul": 3006,
    "cacodemon": 3005, "baron": 3003, "hell_knight": 69,
    "arachnotron": 68, "pain_elemental": 71, "revenant": 66,
    "mancubus": 67, "arch_vile": 64,
    "spider_mastermind": 7, "cyberdemon": 16,
    "stimpack": 2011, "medikit": 2012,
    "green_armor": 2018, "blue_armor": 2019,
    "soul_sphere": 2013, "megasphere": 83,
    "clip": 2007, "shells": 2008, "rocket": 2010, "cell": 2047,
    "shotgun": 2001, "super_shotgun": 82, "chaingun": 2002,
    "rocket_launcher": 2003, "plasma_rifle": 2004,
    "bfg": 2006, "chainsaw": 2005,
    "blue_key": 5, "red_key": 13, "yellow_key": 6,
    "barrel": 2035,
}


def resolve_thing_type(name: str) -> int:
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key in THING_NAMES:
        return THING_NAMES[key]
    try:
        return int(name)
    except ValueError:
        raise ValueError(f"Unknown thing type: {name}")


@dataclass
class Vertex:
    x: float
    y: float
    def to_udmf(self) -> str:
        return f"vertex {{ x = {self.x:.3f}; y = {self.y:.3f}; }}"


@dataclass
class Sector:
    floor: int = 0
    ceiling: int = 128
    light: int = 160
    def to_udmf(self) -> str:
        return (f"sector {{ heightfloor = {self.floor}; heightceiling = {self.ceiling}; "
                f'texturefloor = "FLOOR4_8"; textureceiling = "CEIL3_5"; '
                f"lightlevel = {self.light}; id = 0; }}")


@dataclass
class Sidedef:
    sector: int
    middle: str = "STARTAN2"
    upper: str = "-"
    lower: str = "-"
    def to_udmf(self) -> str:
        return (f"sidedef {{ sector = {self.sector}; "
                f'texturetop = "{self.upper}"; texturemiddle = "{self.middle}"; '
                f'texturebottom = "{self.lower}"; }}')


@dataclass
class Linedef:
    v1: int
    v2: int
    front: int
    back: int = -1
    blocking: bool = True
    def to_udmf(self) -> str:
        parts = f"linedef {{ v1 = {self.v1}; v2 = {self.v2}; sidefront = {self.front};"
        if self.back >= 0:
            parts += f" sideback = {self.back}; twosided = true;"
        parts += f" blocking = {str(self.blocking).lower()}; }}"
        return parts


@dataclass
class Thing:
    x: float
    y: float
    type_id: int
    angle: int = 0
    def to_udmf(self) -> str:
        return (f"thing {{ x = {self.x:.3f}; y = {self.y:.3f}; "
                f"type = {self.type_id}; angle = {self.angle}; "
                "skill1 = true; skill3 = true; skill4 = true; }}")


@dataclass
class RoomTemplate:
    verts: list[tuple[float, float]]
    outdoor: bool = False


def rect(w: float, h: float) -> RoomTemplate:
    hw, hh = w/2, h/2
    return RoomTemplate([(-hw,-hh), (hw,-hh), (hw,hh), (-hw,hh)])


def l_shape(w: float, h: float, n: float = 0.5) -> RoomTemplate:
    hw, hh, nw, nh = w/2, h/2, w/2*n, h/2*n
    return RoomTemplate([(-hw,-hh), (hw,-hh), (hw,nh), (nw,nh), (nw,hh), (-hw,hh)])


def octagon(r: float) -> RoomTemplate:
    return RoomTemplate([(r*math.cos(math.pi/8+i*math.pi/4), r*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)])


def outdoor(w: float, h: float) -> RoomTemplate:
    t = rect(w, h)
    t.outdoor = True
    return t


TEMPLATES = {
    "small_room": rect(256, 256), "medium_room": rect(384, 384),
    "large_room": rect(512, 512), "arena": rect(768, 768),
    "small_l": l_shape(256, 256), "medium_l": l_shape(384, 384),
    "large_l": l_shape(512, 512),
    "small_octagon": octagon(128), "medium_octagon": octagon(192),
    "large_octagon": octagon(256),
    "small_outdoor": outdoor(384, 384), "large_outdoor": outdoor(768, 768),
}


class CompiledMap:
    def __init__(self):
        self.vertices: list[Vertex] = []
        self.sectors: list[Sector] = []
        self.sidedefs: list[Sidedef] = []
        self.linedefs: list[Linedef] = []
        self.things: list[Thing] = []
        self.room_centers: dict[str, tuple[float, float]] = {}
        self.room_sectors: dict[str, int] = {}
        self.room_bounds: dict[str, tuple[float, float, float, float]] = {}

    def add_v(self, x: float, y: float) -> int:
        self.vertices.append(Vertex(x, y))
        return len(self.vertices) - 1

    def to_udmf(self) -> str:
        lines = ['namespace = "zdoom";', ""]
        for v in self.vertices: lines.append(v.to_udmf())
        lines.append("")
        for s in self.sectors: lines.append(s.to_udmf())
        lines.append("")
        for sd in self.sidedefs: lines.append(sd.to_udmf())
        lines.append("")
        for ld in self.linedefs: lines.append(ld.to_udmf())
        lines.append("")
        for t in self.things: lines.append(t.to_udmf())
        return "\n".join(lines)


class Compiler:
    def __init__(self):
        self.map = CompiledMap()
        self.hall_w = 64

    def compile(self, ir: MapIR) -> CompiledMap:
        self.map = CompiledMap()
        if ir.connections:
            self.hall_w = ir.connections[0].width

        east = {c.from_room: c for c in ir.connections}
        west = {c.to_room: c for c in ir.connections}

        x_off, room_x = 0, {}
        for room in ir.rooms:
            room_x[room.id] = x_off
            t = TEMPLATES.get(room.template.value, TEMPLATES["medium_room"])
            w = max(v[0] for v in t.verts) - min(v[0] for v in t.verts)
            x_off += w + 100

        for room in ir.rooms:
            self._room(room, room_x[room.id], 0, room.id in east, room.id in west)
        for conn in ir.connections:
            self._hall(conn)

        return self.map

    def _room(self, room: RoomDefinition, cx: float, cy: float, has_e: bool, has_w: bool):
        t = TEMPLATES.get(room.template.value, TEMPLATES["medium_room"])
        hw = (max(v[0] for v in t.verts) - min(v[0] for v in t.verts)) / 2
        hh = (max(v[1] for v in t.verts) - min(v[1] for v in t.verts)) / 2
        min_x, max_x, min_y, max_y = cx-hw, cx+hw, cy-hh, cy+hh

        self.map.room_bounds[room.id] = (min_x, max_x, min_y, max_y)
        self.map.room_centers[room.id] = (cx, cy)

        si = len(self.map.sectors)
        self.map.room_sectors[room.id] = si
        ceil = 1024 if t.outdoor else room.ceiling_height
        self.map.sectors.append(Sector(room.floor_height, ceil, room.light_level))

        hd, dt, db = self.hall_w/2, cy+self.hall_w/2, cy-self.hall_w/2
        vnw = self.map.add_v(min_x, max_y)
        vne = self.map.add_v(max_x, max_y)
        vse = self.map.add_v(max_x, min_y)
        vsw = self.map.add_v(min_x, min_y)
        vwt = vwb = vet = veb = -1
        if has_w: vwt, vwb = self.map.add_v(min_x, dt), self.map.add_v(min_x, db)
        if has_e: vet, veb = self.map.add_v(max_x, dt), self.map.add_v(max_x, db)

        self._solid(vnw, vne, si)
        if has_e: self._solid(vne, vet, si); self._solid(veb, vse, si)
        else: self._solid(vne, vse, si)
        self._solid(vse, vsw, si)
        if has_w: self._solid(vsw, vwb, si); self._solid(vwt, vnw, si)
        else: self._solid(vsw, vnw, si)

        self._things(room, cx, cy)

    def _hall(self, conn: Connection):
        fb = self.map.room_bounds.get(conn.from_room)
        tb = self.map.room_bounds.get(conn.to_room)
        fc = self.map.room_centers.get(conn.from_room)
        if not fb or not tb or not fc: return

        fs, ts = self.map.room_sectors[conn.from_room], self.map.room_sectors[conn.to_room]
        wx, ex, cy = fb[1], tb[0], fc[1]
        hy = conn.width/2
        ty, by = cy+hy, cy-hy

        hi = len(self.map.sectors)
        self.map.sectors.append(Sector(0, 96, 144))

        vsw = self.map.add_v(wx, by)
        vnw = self.map.add_v(wx, ty)
        vne = self.map.add_v(ex, ty)
        vse = self.map.add_v(ex, by)

        self._twoside(vsw, vnw, hi, fs)
        self._solid(vnw, vne, hi)
        self._twoside(vne, vse, hi, ts)
        self._solid(vse, vsw, hi)

    def _solid(self, v1: int, v2: int, sec: int):
        si = len(self.map.sidedefs)
        self.map.sidedefs.append(Sidedef(sec))
        self.map.linedefs.append(Linedef(v1, v2, si))

    def _twoside(self, v1: int, v2: int, front: int, back: int):
        fi = len(self.map.sidedefs)
        self.map.sidedefs.append(Sidedef(front, "-", "STARTAN2", "STARTAN2"))
        bi = len(self.map.sidedefs)
        self.map.sidedefs.append(Sidedef(back, "-", "STARTAN2", "STARTAN2"))
        self.map.linedefs.append(Linedef(v1, v2, fi, bi, False))

    def _things(self, room: RoomDefinition, cx: float, cy: float):
        for td in room.things:
            try: tid = resolve_thing_type(td.type)
            except ValueError: continue
            for _ in range(td.count):
                if td.x_offset is not None and td.y_offset is not None:
                    x, y = cx+td.x_offset, cy+td.y_offset
                else:
                    s = 64 if td.count == 1 else 100
                    x, y = cx+random.uniform(-s, s), cy+random.uniform(-s, s)
                self.map.things.append(Thing(x, y, tid, random.randint(0, 359)))


def build_wad(compiled: CompiledMap, name: str = "MAP01") -> bytes:
    textmap = compiled.to_udmf().encode()
    lumps = [(name, b""), ("TEXTMAP", textmap), ("ENDMAP", b"")]

    off, entries, data = 12, [], b""
    for n, d in lumps:
        entries.append((off, len(d), n))
        data += d
        off += len(d)

    dir_off = off
    directory = b""
    for o, s, n in entries:
        directory += struct.pack("<II", o, s) + n.ljust(8, '\x00')[:8].encode()

    return b"PWAD" + struct.pack("<II", len(lumps), dir_off) + data + directory


def demo_ir() -> MapIR:
    return MapIR(
        name="MAP01", title="Hello Doom",
        rooms=[
            RoomDefinition(id="start", template=RoomType.MEDIUM_ROOM,
                things=[ThingPlacement(type="player_start", count=1),
                        ThingPlacement(type="shotgun", count=1, x_offset=32)]),
            RoomDefinition(id="arena", template=RoomType.LARGE_OCTAGON,
                things=[ThingPlacement(type="imp", count=5),
                        ThingPlacement(type="stimpack", count=2)]),
        ],
        connections=[Connection(from_room="start", to_room="arena")]
    )


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo")
    d.add_argument("-o", "--output", default="demo.wad")

    g = sub.add_parser("from-ir")
    g.add_argument("input")
    g.add_argument("-o", "--output")

    s = sub.add_parser("schema")

    args = p.parse_args()

    if args.cmd == "demo":
        ir = demo_ir()
        wad = build_wad(Compiler().compile(ir), ir.name)
        Path(args.output).write_bytes(wad)
        print(f"Created: {args.output}")

    elif args.cmd == "from-ir":
        data = json.loads(Path(args.input).read_text())
        ir = MapIR.model_validate(data)
        errs = ir.validate_connections()
        if errs:
            for e in errs: print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        wad = build_wad(Compiler().compile(ir), ir.name)
        out = args.output or f"{ir.name.lower()}.wad"
        Path(out).write_bytes(wad)
        print(f"Created: {out}")

    elif args.cmd == "schema":
        print(json.dumps(MapIR.model_json_schema(), indent=2))


if __name__ == "__main__":
    main()
