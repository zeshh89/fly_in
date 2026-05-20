# Drone Routing Simulation

A multi-drone routing and congestion simulation project built in Python using Pygame.

> Created by **jose-an2** for the 42 Network cursus.

---

## Overview

This project simulates autonomous drone movement inside a graph-based transport network.

The system includes:

- Weighted pathfinding using Dijkstra
- Multi-path route generation
- Hub capacity management
- Connection capacity management
- Traffic congestion simulation
- Turn-based movement engine
- Real-time rendering with interpolation
- Support for restricted and priority zones

The objective is to route multiple drones from a start hub to an end hub while respecting traffic and infrastructure constraints.

---

## Smart Pathfinding

The project uses a weighted Dijkstra algorithm. Routing decisions consider:

- Blocked zones
- Restricted zones
- Priority zones
- Hub capacities
- Dynamic routing penalties

The system also generates multiple alternative routes to distribute traffic across the graph.

---

## Congestion Simulation

The simulation engine handles:

- Hub occupancy
- Connection occupancy
- Movement conflicts
- Waiting turns
- Restricted area delays

This creates realistic traffic flow behavior similar to pipelines or transport networks.

---

## Routing Logic

The pathfinding system assigns movement cost using:

- Zone type
- Hub capacity
- Dynamic penalties

Large hubs are preferred because they reduce congestion risk.

The simulation itself then enforces:

- Occupancy limits
- Movement timing
- Connection capacities

---

## Real-Time Visualization

The renderer uses Pygame and includes:

- Animated drone interpolation
- Scalable graph rendering
- Colored zones
- Live turn counter
- Smooth drone movement

---

## Map File Format

The simulation reads a `map.txt` file describing the graph.

### Valid Map Structure

A valid map must contain:

- Exactly one `start_hub`
- Exactly one `end_hub`
- At least one valid path between them

### Hub Syntax

```
hub: NAME X Y [metadata]
```

**Example:**

```
hub: waiting_area1 1 1 [color=blue max_drones=4]
```

**Special Hub Types:**

```
start_hub: start 0 0 [color=green max_drones=12]
end_hub: goal 9 0 [color=green max_drones=12]
```

### Metadata

Metadata is written inside brackets `[...]`.

| Key | Description |
|---|---|
| `color` | Visual color |
| `max_drones` | Hub capacity |
| `zone` | Zone behavior |

### Zone Types

| Zone Type | Behavior |
|---|---|
| `normal` | Standard movement |
| `restricted` | Adds movement delay |
| `priority` | Lower routing cost |
| `blocked` | Cannot be traversed |

### Connection Syntax

Connections define graph edges:

```
connection: hubA hubB
```

**Example:**

```
connection: gate1 waiting_area1
```

### Example Map

```
start_hub: start 0 0 [color=green max_drones=12]
hub: gate1 1 0 [color=orange max_drones=1]
hub: waiting_area1 1 1 [color=blue max_drones=4]
hub: bypass 2 1 [zone=priority color=cyan max_drones=3]
hub: tunnel 3 0 [zone=restricted color=red max_drones=2]
end_hub: goal 4 0 [color=green max_drones=12]

connection: start gate1
connection: gate1 waiting_area1
connection: waiting_area1 bypass
connection: bypass tunnel
connection: tunnel goal
```

---

## Project Architecture

### Core Components

| Module | Responsibility |
|---|---|
| `parser` | Reads and validates maps |
| `pathfinding` | Computes routes |
| `scheduler` | Assigns drones to paths |
| `simulation` | Simulates traffic |
| `renderer` | Displays the simulation |

### Technologies Used

- Python
- Pygame
- Graph algorithms
- Dijkstra shortest-path routing

---

## Notes About AI Usage

Artificial Intelligence tools were used for:

- Debugging assistance
- Error correction
- Understanding algorithmic concepts
- Improving architecture decisions
- Learning foundations that were not yet fully mastered

All design, implementation, and integration work was carried out manually as part of the learning process.
