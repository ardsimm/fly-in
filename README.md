*This project has been created as part of the 42 curriculum by smenard.*

# Fly-in

## Description

Fly-in routes a fleet of drones through a network of zones, from a start hub to an end hub, in
as few simulation turns as possible.

The program reads a map file describing zones, connections and the number of drones. It plans a
path for every drone, respecting zone capacities, link capacities and zone types, and prints the
moves turn by turn. Then it opens a window that animates the simulation.

Rules, in short:

- Every drone starts in the start hub. The simulation ends when all of them reach the end hub.
- A zone holds at most `max_drones` drones (default 1). Start and end hubs have no limit.
- A connection is used by at most `max_link_capacity` drones per turn (default 1).
- Zone types: `normal` (1 turn to enter), `priority` (1 turn, preferred), `restricted` (2 turns,
  the drone spends the turn in between on the connection), `blocked` (never entered).
- Each turn, a drone moves to a neighbouring zone, takes off towards a restricted zone, or waits.
  All moves of a turn are simultaneous, and a zone or connection vacated during a turn is
  available to another drone in that same turn.

The project is written in Python 3.12, fully object-oriented and type-checked. It uses no graph
library: all pathfinding is hand-written.

## Instructions

### Requirements

- Python 3.12 or later (the code uses PEP 701 f-strings and `enum.StrEnum`)
- [uv](https://docs.astral.sh/uv/)

### Installation and usage

```sh
make install                                          # create .venv and install the dependencies
make run                                              # run data/maps/easy/01_linear_path.txt
make run MAP=data/maps/hard/02_capacity_hell.txt      # run another map
uv run python -m src path/to/map.txt                  # same, without make
```

The moves are printed on stdout, one line per turn. The visualiser window opens afterwards;
close it or press `q` to exit. Errors are printed on stderr and the program exits with status 1.

### Other Makefile rules

| Rule | Effect |
|---|---|
| `make debug MAP=...` | Run the program under `pdb` |
| `make lint` | `flake8 .` and `mypy .` with the flags required by the subject |
| `make lint-strict` | `flake8 .` and `mypy . --strict` |
| `make black` | Format the code (79 columns) |
| `make clean` | Remove `__pycache__` and `.mypy_cache` |
| `make fclean` | `clean`, and remove `.venv` |
| `make re` | `fclean`, then `install` |

### Map format

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

The first line is `nb_drones`. Zones are `start_hub:`, `end_hub:` or `hub:`, followed by a name
(no dashes or spaces), integer coordinates and optional metadata. Connections link two zones
defined earlier. `#` starts a comment. Any error stops the program with the offending line and
the cause.

## Example

Input, `data/maps/medium/03_priority_puzzle.txt`:

```
nb_drones: 5
start_hub: start 0 0 [color=green]
hub: slow_path1 1 -1 [zone=restricted color=red]
hub: slow_path2 2 -1 [color=red]
hub: fast_junction 1 0 [zone=priority color=blue max_drones=2]
hub: fast_path 2 0 [zone=priority color=blue]
hub: merge_point 3 0 [color=yellow max_drones=3]
end_hub: goal 4 0 [color=green]
connection: start-slow_path1
connection: start-fast_junction
connection: slow_path1-slow_path2
connection: slow_path2-merge_point
connection: fast_junction-fast_path
connection: fast_path-merge_point
connection: merge_point-goal [max_link_capacity=2]
```

Output (6 turns, the optimum for this map):

```
D1-fast_junction D2-start-slow_path1
D1-fast_path D2-slow_path1 D3-fast_junction D4-start-slow_path1
D1-merge_point D2-slow_path2 D3-fast_path D4-slow_path1 D5-fast_junction
D1-goal D2-merge_point D3-merge_point D4-slow_path2 D5-fast_path
D2-goal D3-goal D4-merge_point D5-merge_point
D4-goal D5-goal
```

Each line is a turn, and each `D<ID>-<zone>` is a move; drones that do not move are omitted.
`D2-start-slow_path1` means D2 is in flight on the connection towards the restricted zone
`slow_path1`, which it reaches on the next turn. Three drones take the fast lane, one per turn;
D2 and D4 take the slower restricted lane in parallel, and all five arrive in 6 turns.

Errors:

```
$ uv run python -m src data/maps/claude/parser/22_invalid_zone.txt
Error in line: "hub: a 1 0 [zone=lava]":
Invalid zone lava, options:['normal', 'restricted', 'priority', 'blocked']

$ uv run python -m src data/maps/claude/solver/10_unreachable_goal.txt
Error: map is not solvable
```

## Algorithm

### Pipeline

1. **Parsing** (`src/parser/`). The map is turned into `Node` and `Connection` objects. Each node
   holds the list of its connections, so the graph is an adjacency list. The connections of each
   node are sorted once, by the priority of the zone they lead to.
2. **Solvability check** (`Simulation.check_solvable`). A plain BFS from the start hub to the end
   hub, ignoring capacities and skipping blocked zones. If it fails, the map is reported as not
   solvable.
3. **Planning** (`Simulation.cooperative_bfs`), described below.
4. **Validation and output** (`Simulation.get_turns`, `print_turns`). The planned paths are
   replayed turn by turn; any move that breaks a capacity or zone rule raises an error instead
   of being printed.
5. **Visualisation** (`src/visualiser/`).

### Cooperative pathfinding with a reservation table

Drones are planned one after the other. The positions of the drones already planned are stored
in a shared reservation table, `allocation_table[turn][zone or connection] = number of drones`,
and every new drone searches for its path around them. This is the cooperative pathfinding
approach (prioritized planning with a space-time reservation table).

For one drone, the search explores states `(zone, turn)`. A heap ordered by turn makes it a
breadth-first search in time: the first path found to the end hub is the earliest arrival the
search can find for this drone. From a zone at turn `t`, for each connection:

- blocked zones are skipped;
- the connection must have room at turn `t`: the drones starting a move on it at `t` must be
  fewer than `max_link_capacity`;
- for a normal or priority zone, the zone must have room at turn `t + 1`, and the drone reaches
  it at `t + 1`;
- for a restricted zone, the zone must have room at turn `t + 2`. The drone is on the connection
  at `t + 1` and in the zone at `t + 2`. The in-flight state has a single successor, so a drone
  can never wait on a connection. A landing frees the connection, so another drone may take off
  on it during the same turn.

If a move is refused because of capacity, the drone may also wait in its zone until `t + 1`.
Because the connections are sorted by priority, priority zones are explored first and win any
tie between routes of the same duration.

When the end hub is reached, the path is rebuilt from the predecessor of each state and written
to the reservation table: each zone at each turn, and each connection on the turn a drone takes
off on it. The start and end hubs have no capacity limit.

### Why this approach

All drones are identical and start together, so what matters is spreading them over the
available routes and timing them through the bottlenecks. Planning drones one by one against a
reservation table does both: the first drones take the fastest routes, and the next ones either
wait for a free slot or take a longer route when it arrives earlier. It is simple, it never
produces a conflict by construction, and it reaches the optimum on every map shipped with the
subject.

It is a greedy method, though: a drone never delays itself to let the others pass, so on some
hand-made traps (`data/maps/claude/solver/01_braess_cross.txt`, `02_selfish_detour.txt`) the
result is longer than the optimum. An exact alternative is a maximum flow on a time-expanded
graph (one copy of each zone per turn, capacities on zones and links), searching for the
smallest number of turns that carries every drone.

### Results

| Map | Drones | Turns | Optimum |
|---|---|---|---|
| easy/01_linear_path | 2 | 4 | 4 |
| easy/02_simple_fork | 4 | 4 | 4 |
| easy/03_basic_capacity | 4 | 4 | 4 |
| medium/01_dead_end_trap | 5 | 8 | 8 |
| medium/02_circular_loop | 6 | 10 | 10 |
| medium/03_priority_puzzle | 5 | 6 | 6 |
| hard/01_maze_nightmare | 8 | 13 | 13 |
| hard/02_capacity_hell | 12 | 16 | 16 |
| hard/03_ultimate_challenge | 15 | 26 | 26 |
| challenger/01_the_impossible_dream | 25 | 43 | 43 |

### Complexity, caching and memory

With V zones, E connections, N drones and T turns in the result:

- **Planning one drone**: each zone is expanded once, at its earliest arrival, plus one state
  per turn spent waiting. Each expansion scans the connections of the zone and pushes onto a
  heap, which gives roughly O((E + W) log(E + W)), where W is the number of waiting states.
- **All drones**: N searches. On maps with a single bottleneck, drone k waits about k turns,
  so the total grows as O(N^2). On the shipped maps, planning takes a few milliseconds.
- **Caching**: nothing is recomputed. Each drone is planned exactly once, and the reservation
  table acts as the cache of every earlier path. The neighbour order is computed once, when
  parsing.
- **Memory**: the reservation table holds at most one entry per zone and connection per turn,
  O(T(V + E)), and the paths hold one step per drone per turn, O(NT).

Measured on the solver alone (planning and validation, Python 3.12):

| Map | Drones | Turns | Time | Peak memory |
|---|---|---|---|---|
| challenger/01_the_impossible_dream | 25 | 43 | 0.01 s | - |
| 30x30 grid, random capacities | 300 | 209 | 1.7 s | 13 MB |
| 3-zone chain | 1,000 | 1,002 | 0.7 s | 5 MB |
| 3-zone chain | 2,000 | 2,002 | 2.8 s | 19 MB |
| 3-zone chain | 4,000 | 4,002 | 13.0 s | 71 MB |

The chain is the worst case: every drone waits in the start hub for the previous one, so time and
memory grow with the square of the number of drones. Skipping the start-hub waits in the search
(starting each drone at the first turn a move out of the start is possible) would remove most of
this cost.

## Visual representation

After printing the moves, the program opens a pygame window that replays the simulation.

- **Zones** are circles. The fill uses the `color` given in the map (around 950 color names
  from `data/colors.json`, then pygame's own names, then black). The border shows the zone type:
  white for normal, blue for priority, red for restricted, black for blocked. The capacity
  (`max_drones`) is written in the center, and the name appears when the mouse hovers the zone.
- **Connections** are lines labelled with their `max_link_capacity`.
- **Drones** are circles labelled with their ID. They glide from one zone to the next, and a
  drone flying towards a restricted zone stops halfway along the connection for its in-flight
  turn.

Controls:

| Key | Action |
|---|---|
| Right / Left arrow | Next / previous turn |
| Space | Start or stop the automatic replay |
| Up / Down arrow | Faster / slower replay |
| `r` | Back to the first turn |
| `q` or closing the window | Quit |

Stepping through the turns makes the scheduling visible: where drones queue in front of a
bottleneck, when a drone waits, which drones take a detour, and how restricted zones slow a lane
down. Stepping backwards helps to check a single turn against the printed output.

## Project structure

```
src/
  __main__.py          entry point (Main)
  models/              Node, Connection, Drone, Map
  enums/               NodePriority (zone types)
  parser/              map file parser and ParsingError
  simulation/          solvability check, cooperative planning, validation, output
  visualiser/          pygame window, drawable elements, color/font/mouse managers
data/
  colors.json          color names for the visualiser
  maps/                maps shipped with the subject (easy, medium, hard, challenger)
  maps/custom/         our own edge-case maps
  maps/claude/         test maps for the parser, the solver and restricted zones
```

## Resources

- Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms*: breadth-first search, shortest
  paths, maximum flow.
- D. Silver, *Cooperative Pathfinding*, AIIDE 2005: cooperative A* and space-time reservation
  tables, the idea behind the planner.
- R. Stern et al., *Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks*, SoCS 2019:
  overview of multi-agent pathfinding.
- G. Sharon et al., *Conflict-Based Search for Optimal Multi-Agent Pathfinding*, Artificial
  Intelligence, 2015: an optimal alternative to prioritized planning.
- L. R. Ford, D. R. Fulkerson, *Flows in Networks*, 1962: flows over time and time-expanded
  networks.
- Python documentation: [heapq](https://docs.python.org/3/library/heapq.html),
  [collections.deque](https://docs.python.org/3/library/collections.html#collections.deque).
- [pygame-ce documentation](https://pyga.me/docs/).
- [PEP 257](https://peps.python.org/pep-0257/) and the
  [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings.

### Use of AI

Claude (Anthropic), through Claude Code, was used for:

- **Reviews and testing**: audits of the code against the subject, stress tests of the parser
  and the solver with random maps, and diagnosis of bugs (restricted zones, output format,
  error handling). The reports, issues and todo lists are kept in `claude/`, and the test maps
  in `data/maps/claude/`.
- **Solver tuning**: identifying why two medium maps missed their optimum after the subject's
  update of the restricted-connection rule. The change itself (two conditions in
  `cooperative_bfs`) was reviewed and applied by hand.
- **Documentation**: the docstrings and this README.

The parser, the solver and the visualiser were designed and written by hand. `CLAUDE.md`
describes the project for the assistant.
