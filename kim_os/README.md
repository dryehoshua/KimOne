# Kim OS

Kim OS is the modular operating layer for Kim Live.

It is not the intelligence, not the knowledge base and not the tools. It is the skeleton that loads an intelligence profile, attaches behavior, routes memory, exposes tools and serves the UI/API.

## Layers

```text
Kim OS
├── kernel/        runtime, server, routing, auth, scheduler
├── behavior/      main behavior prompt and interaction style
├── knowledge/     knowledge routing contracts and memory policies
├── modules/       module registration and dependency boundaries
└── tools/         external executable capabilities via kimtools/
```

## Separation Rule

- `kernel` decides how Kim runs.
- `behavior` decides how Kim behaves.
- `intelligence` decides whose intelligence Kim carries.
- `knowledge` stores learned concepts, client preferences, company doctrine and domain memory.
- `tools` execute actions.

No layer should impersonate another layer.

## Current Reality

`kim_live/server.py` is still the production monolith. It currently contains kernel, behavior, tool routing, knowledge capture and several tools in one file.

The migration rule is:

1. New features must be added as modules/tools/manifests, not directly as random `server.py` blocks.
2. Existing code is extracted module by module.
3. `server.py` remains a compatibility kernel until the front end and runtime can depend on `kim_os` directly.

## Current Kernel

Runtime:

`/Users/dryehoshuapython/.kim_live/server.py`

Source:

`/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kim_live/server.py`

Kernel manifest:

`kim_os/kernel/kernel_manifest.json`

## Intelligence

Default intelligence package:

`intelligences/miu`

MIU is the loaded intelligence of Dr. Yehoshua: Tesca, Ignis, AI People, personal preferences, client-specific style and learned operating philosophy.

Kim should not hardcode MIU knowledge inside tools. Tools are reusable; MIU is portable loaded intelligence.

