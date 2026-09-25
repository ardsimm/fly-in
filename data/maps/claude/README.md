# Claude test maps

Maps written to stress the solver and the parser. Results and analysis are in
`claude/reports/report_0_20260925-031836.md`. "Optimal" below is the minimum number of turns
(moves of the last drone), computed with a time-expanded max-flow; the program's
"Solution found in N turns" line currently prints optimal + 1 (see the report).

None of these maps use `zone=restricted` (not supported yet).

## solver/

| Map | Purpose | Expected |
|---|---|---|
| 01_braess_cross.txt | Short and long lane joined by a cross link that every drone greedily uses | 23 turns |
| 02_selfish_detour.txt | Single-capacity door next to a +2 detour; no drone takes the detour on its own | 16 turns |
| 03_tie_break.txt | Two equally short routes, one blocks the next drone | 3 turns |
| 04_priority_tie.txt | Same length through a priority zone or a normal zone | drone goes through `fast_lane` |
| 05_direct_link_many.txt | start-goal link of capacity 1, 50 drones | 50 turns |
| 06_parallel_lanes.txt | Three disjoint lanes of lengths 3/4/5 | 13 turns |
| 07_dead_end_pockets.txt | Corridor with dead-end pockets | 9 turns, no drone in a pocket |
| 08_zero_drones.txt | `nb_drones: 0` | clean parse error |
| 09_self_loop.txt | `a-a` connection before the real ones | reject cleanly or ignore, no crash |
| 10_unreachable_goal.txt | goal in another component | "not solvable", exit 1 |
| 11_isolated_hub.txt | Hub with no connection | 3 turns |
| 12_wide_capacity.txt | Capacities of 20 everywhere | 3 turns |
| 13_goal_link_bottleneck.txt | Links into the goal of capacity 1 and 2 | 5 turns |
| 14_grid_200_drones.txt | 12x12 grid, random capacities, 200 drones | 121 turns |
| 15_grid_1000_drones.txt | Same grid, 1000 drones (scaling) | 521 turns |

## parser/

| Map | Subject rule | Expected |
|---|---|---|
| 01_blocked_zone.txt | `blocked` is a valid zone type | parse, avoid `b` |
| 02_max_drones_zero.txt | capacities are positive integers | parse error |
| 03_link_capacity_zero.txt | capacities are positive integers | parse error |
| 04_hub_named_like_start.txt | zone names are unique | parse error |
| 05_hub_named_like_end.txt | zone names are unique | parse error |
| 06_unknown_line.txt | syntax must be respected | parse error on `hubb:` |
| 07_duplicate_metadata_key.txt | metadata must be syntactically valid | parse error |
| 08_reversed_duplicate_connection.txt | a-b and b-a are duplicates | parse error |
| 09_connection_before_hub.txt | connections link previously defined zones | parse error |
| 10_negative_coords.txt | coordinates are integers | 2 turns |
| 11_crlf.txt | Windows line endings | 3 turns |
| 12_inline_comments.txt | `#` starts a comment | 3 turns |
| 13_nb_drones_negative.txt | positive integer | parse error |
| 14_nb_drones_not_int.txt | positive integer | parse error |
| 15_nb_drones_not_first.txt | first line is nb_drones | parse error |
| 16_missing_end.txt | exactly one end hub | parse error |
| 17_two_starts.txt | exactly one start hub | parse error |
| 18_empty.txt | - | parse error |
| 19_only_comments.txt | - | parse error |
| 20_unclosed_metadata.txt | metadata must be syntactically valid | parse error |
| 21_unknown_metadata_key.txt | metadata must be syntactically valid | parse error |
| 22_invalid_zone.txt | invalid zone type is a parse error | parse error |
| 23_float_coords.txt | integer coordinates | parse error naming the right coordinate |
| 24_tab_separated.txt | - | parse error on the hub line (or accept tabs) |
| 25_extra_token.txt | - | parse error |
| 26_dash_in_name.txt | no dashes in names | parse error |
| 27_unknown_hub_in_connection.txt | connections link defined zones | parse error |
| 28_nb_drones_huge.txt | any number of drones | 5000 drones solved |
| 29_start_metadata_ignored.txt | max_drones on start/end is ignored | 2 turns |
| 30_empty_metadata.txt | - | parse (or clean error) |
| 31_unicode_names.txt | any character except dash and space | 2 turns |
| 32_zone_uppercase.txt | - | clean error (or accept) |
| 33_no_space_after_colon.txt | - | parse error on the hub line |
| 34_self_loop_first.txt | - | no false "duplicate" on later links |
| 35_self_loop_last.txt | - | no crash |
| 36_start_end_same_node.txt | zone names are unique | parse error |
