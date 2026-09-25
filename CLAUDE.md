# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Fly-in (42 curriculum project; subject in `private/en.md`, gitignored). Parse a map of zones and
connections, route `nb_drones` drones from `start_hub` to `end_hub` in as few simulation turns as
possible while respecting zone capacity (`max_drones`) and link capacity (`max_link_capacity`), and
show the result visually (pygame-ce window). Map format, occupancy rules, turn mechanics, the
required output format (`D<ID>-<zone>` per move, one line per turn) and per-map turn targets are
all in the subject; `data/maps/` holds the provided maps (`easy/`, `medium/`, `hard/`,
`challenger/`) plus our own edge-case maps in `data/maps/custom/`.

Hard constraints from the subject that apply to every change:

- Python >= 3.10, fully object-oriented, type hints everywhere, PEP 257 docstrings.
- No graph libraries (networkx, graphlib, ...): all pathfinding is hand-written.
- Must pass flake8 and mypy; no unhandled exception may reach the user (the program is
  considered non-functional if it crashes), use context managers for resources.
- Parse errors must stop the program with a clear message naming the line and the cause.

## Commands

```sh
make install                  # uv sync
make run                      # uv run python -m src $(MAP)   (default MAP=data/maps/easy/01_linear_path.txt)
make run MAP=data/maps/hard/02_capacity_hell.txt
make debug MAP=...            # same, under pdb
make build                    # writes ./fly-in, a bash wrapper around `uv run python -m src "$@"`
make lint                     # flake8 . + mypy src --warn-return-any --warn-unused-ignores
                              #   --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
make lint-strict              # flake8 . + mypy . --strict
make black                    # black --line-length 79 .
make clean / fclean           # remove caches, output dirs and ./fly-in / also remove .venv
```

The program opens a pygame window after printing the solution; close it or press `q` to exit.

There is no test suite in this repo (the subject says tests are for your own verification and are
not submitted/graded). Verify changes by running the maps under `data/maps/` and comparing the turn
count against the targets in the subject (chapter VII.7).

## Architecture

Pipeline, driven by `src/__main__.py` (`Main.main`):

1. `Parser.parse(str) -> Map` (`src/parser/parser.py`). Builds `Node` and `Connection` objects,
   appends each `Connection` to both of its nodes' `connections` lists (the graph is an adjacency
   list living on the nodes themselves), creates the `Drone` objects, and shifts all coordinates so
   the minimum x/y is 0 (the visualiser relies on that). Zone type is stored as an integer
   `Node.priority` (blocked=-1, restricted=0, normal=1, priority=2), not as a string. Every failure
   is surfaced as `ParsingError`.
2. `Simulation.check_solvable(map)` runs a plain BFS start -> end; raises `PathNotFoundError`.
3. `Simulation.cooperative_bfs(map)` is the actual solver: a time-expanded BFS run once per drone,
   in order, against a shared reservation table `allocation_table[turn] = (node_occupancy,
   connection_occupancy)`. Each drone's path is reconstructed from `prev_nodes[(turn, node)]` and
   then reserved in the table so later drones route around it. Waiting in place is modelled as a
   `(node, None)` predecessor. Result is written to `drone.path` (one node per turn).
4. `Simulation.get_turns(map, paths)` replays the paths turn by turn and raises
   `InvalidMoveError` on zone over-capacity.
5. `Visualiser(map).render()` (`src/visualiser/`) animates `drone.path` for each drone. It is a list
   of `Element` subclasses (`NodeElement`, `ConnectionElement`, `DroneElement`) sorted by
   `z_index`, each with `update(dt, combined_dt)` / `draw()`. `CoordinateManager` maps map coords
   to pixels; `ColorManager` resolves free-form color names through `data/colors.json` (loaded via a
   relative path, so run from the repo root).

`src/graph/`, `src/solver/` and `src/display/` are abstract scaffolding (`Graph`, `Solver` ABC,
`Display` ABC) not yet wired into the pipeline.

Things to keep in mind when touching the solver/simulation:

- `Node` and `Connection` are used as dict keys in the reservation tables. `Connection` is a frozen
  dataclass with an order-independent `__hash__`; `Node` uses identity hashing.
- `Node.drones_count` and `Drone.done` are mutable state set during parsing/solving.
- Restricted zones cost 2 turns and the drone must be shown in flight on the connection
  (`D<ID>-<connection>`) during the intermediate turn; start and end hubs have no capacity limit.
- The current stdout output is debug-oriented and does not yet follow the subject's output format.

## Claude-authored reports, todos, and issues

Reports (audits, reviews, etc.) written by Claude go under `claude/reports/`, named
`report_[number]_[timestamp].md` -- `number` is a sequential index starting at 0, `timestamp` is
`YYYYMMDD-HHMMSS` (local time at creation). Example: `claude/reports/report_0_20260823-193657.md`.

Todo lists follow the same convention under `claude/todo/`, named `todo_[number]_[timestamp].md`.

Draft GitHub issues (write-up + checklist, ready to paste as an issue body) follow the same
convention under `claude/issues/`, named `issue_[number]_[timestamp].md`, and end with the line
`*Issue discovered and written by claude*`.

These directories are tracked in git (not ignored).

## Working guidelines

- Never generate code unless directly asked to do so.
- When generating code, follow flake8's norm and the 79-column black style. Run `make lint-strict`
  (flake8 + mypy --strict) to check compliance before considering a change done.
- Never use emojis -- not in code, comments, markdown, or anywhere else.
