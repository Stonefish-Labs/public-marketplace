# IR Schema Reference

Full schema for Doom map intermediate representation. Read this when you need
exact field names, available templates, or valid thing types.

## Schema Structure

```json
{
  "name": "MAP01",
  "title": "Human Readable Title",
  "author": "Author Name (optional)",
  "rooms": [...],
  "connections": [...]
}
```

## Room Definition

```json
{
  "id": "unique_room_id",
  "template": "medium_room",
  "floor_height": 0,
  "ceiling_height": 128,
  "light_level": 160,
  "things": [
    {"type": "player_start", "count": 1, "x_offset": 0, "y_offset": 0}
  ],
  "is_secret": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier, snake_case |
| `template` | string | Yes | Room template name |
| `floor_height` | int | No | Default 0 |
| `ceiling_height` | int | No | Default 128 |
| `light_level` | int | No | 0-255, default 160 |
| `things` | array | No | Thing placements |
| `is_secret` | bool | No | Default false |

## Room Templates

| Template | Shape | Dimensions |
|----------|-------|------------|
| `small_room` | Rectangle | 256×256 |
| `medium_room` | Rectangle | 384×384 |
| `large_room` | Rectangle | 512×512 |
| `arena` | Rectangle | 768×768 |
| `small_l` | L-shape | 256×256 |
| `medium_l` | L-shape | 384×384 |
| `large_l` | L-shape | 512×512 |
| `small_octagon` | 8-sided | r=128 |
| `medium_octagon` | 8-sided | r=192 |
| `large_octagon` | 8-sided | r=256 |
| `small_outdoor` | Open sky | 384×384 |
| `large_outdoor` | Open sky | 768×768 |

## Connection Definition

```json
{
  "from_room": "room_id",
  "to_room": "room_id",
  "width": 64,
  "is_door": false,
  "is_secret": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from_room` | string | Yes | Source room ID |
| `to_room` | string | Yes | Target room ID |
| `width` | int | No | Hallway width (48-128), default 64 |
| `is_door` | bool | No | Add door, default false |
| `is_secret` | bool | No | Secret passage, default false |

## Thing Types

### Player Starts

| Type | Description |
|------|-------------|
| `player_start` | Player 1 start (required) |
| `player_2_start` | Co-op player 2 |
| `player_3_start` | Co-op player 3 |
| `player_4_start` | Co-op player 4 |
| `deathmatch_start` | DM spawn point |

### Monsters

| Type | Threat | Notes |
|------|--------|-------|
| `zombieman` | Low | Hitscan, pistol |
| `shotgun_guy` | Low-Mid | Hitscan, shotgun |
| `imp` | Low | Projectile |
| `demon` | Low-Mid | Melee only |
| `spectre` | Low-Mid | Invisible demon |
| `lost_soul` | Low | Floating, charges |
| `cacodemon` | Mid | Floating, projectile |
| `hell_knight` | Mid-High | Baron-lite |
| `baron` | High | Tanky, projectile |
| `arachnotron` | Mid | Plasma rapid-fire |
| `pain_elemental` | Mid | Spawns lost souls |
| `revenant` | Mid-High | Homing missiles |
| `mancubus` | Mid-High | Fireball spread |
| `arch_vile` | Very High | Revives, hitscan attack |
| `spider_mastermind` | Boss | Chaingun, huge |
| `cyberdemon` | Boss | Rockets, massive HP |

### Weapons

| Type | Tier |
|------|------|
| `shotgun` | Early |
| `super_shotgun` | Mid |
| `chaingun` | Early-Mid |
| `rocket_launcher` | Mid |
| `plasma_rifle` | Late |
| `bfg` | Late/Boss |
| `chainsaw` | Melee |

### Pickups

| Type | Effect |
|------|--------|
| `stimpack` | +10 health |
| `medikit` | +25 health |
| `green_armor` | 100 armor |
| `blue_armor` | 200 armor |
| `soul_sphere` | +100 health (max 200) |
| `megasphere` | 200 health + 200 armor |

### Ammo

`clip`, `bullets`, `shells`, `box_of_shells`, `rocket`, `box_of_rockets`, `cell`, `cell_pack`

### Keys

`blue_key`, `red_key`, `yellow_key`, `blue_skull`, `red_skull`, `yellow_skull`

### Decorations

`barrel` (explosive), `pillar`, `candelabra`
