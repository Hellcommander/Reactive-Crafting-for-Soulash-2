# Reactive Crafting

Terrain-reactive throwables crafted from the ground you stand on.

| Item | Craft terrain | Throw effect | Combo notes |
|---|---|---|---|
| Muddy Waterskin | plowed/mud/clay | Wet puddles (`411`) | Sets up water synergies |
| Sand Pouch | sand | Blind + sand (`430`) | Slows footing |
| Ember Pouch | ash | Fire + flames (`561`) | Ignites oil webs |
| Snow Pouch | snow | Freeze + snow | Slows / chill |
| Oil Flask | clay floor + Transmutation Oil | Cobwebs (`1066`) immobilize | Ember turns webs into flame |
| Salt Sack | sand | Sand cover (`430`) | Dries wet ground |

Recovered/reconstructed to **v0.4.0** after the 8/14 data wipe.


## v0.6.0: 20-level utility skill
The skill unlocks crafting recipes (milestone reward `recipe` = the item id). Stats only at levels 11-20; mastery at 20.
| Lvl | Unlock |
|---|---|
| 1 | Recipe: Muddy Waterskin |
| 2 | Recipe: Sand Pouch |
| 3 | Field Pack |
| 4 | Recipe: Salt Sack |
| 5 | Thrifty Hands |
| 6 | Recipe: Snow Pouch |
| 7 | Efficient Crafting |
| 8 | Recipe: Ember Pouch |
| 9 | Terrain Reader |
| 10 | Recipe: Oil Flask |
| 11 | Pack Mule (first statistic) |
| 12 | Recipe: Greater Ember Pouch |
| 13 | Resourceful |
| 14 | Recipe: Quagmire Skin |
| 15 | Practiced Hands |
| 16 | Recipe: Glacial Pouch |
| 17 | Steady Throw |
| 18 | Recipe: Brine Flask |
| 19 | Deep Pockets |
| 20 | Recipe: Volatile Bundle, Reactive Crafting Mastery |
Removed skill.json (bundled dump, not a game file). Verify: recipe gating of craftable items, throw abilities keep `skill` only for XP, no crafting exp source id known.
