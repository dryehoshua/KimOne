# KimOne Modularization Plan

## Goal

Turn Kim from a single large `server.py` into portable Lego pieces:

```text
Kim OS kernel
Behavior prompt
Loaded intelligence: MIU
Knowledge libraries
Tools
External libraries
Frontend shell
```

## Target Layout

```text
KimOne/
├── kim_os/
│   ├── kernel/
│   ├── behavior/
│   ├── knowledge/
│   └── modules/
├── intelligences/
│   └── miu/
├── kimtools/
│   ├── ignis_financials/
│   ├── diagrams/
│   ├── tradingview/
│   └── registry/
└── kim_live/
    └── server.py  # legacy compatibility kernel during migration
```

## Migration Order

1. Freeze `server.py` as legacy kernel.
2. Extract tool contracts first.
3. Extract MIU knowledge and librarian policy.
4. Extract behavior prompt.
5. Extract scheduler and tool router.
6. Build new frontend over module registry.
7. Reduce `server.py` to startup, auth, router and compatibility glue.

## Non-Negotiables

- Finance state remains structured and ledger-based.
- Knowledge is not stored inside tools.
- Tools never claim success without verifiable evidence.
- MIU is portable and can be copied to another machine.
- New client/company intelligence should be a package, not a fork of Kim.

## First Extracted Tool

`kimtools/ignis_financials` is the first formal tool package.

## First Intelligence Package

`intelligences/miu` is the first loaded intelligence package.

## What Changes Now

New features should land in one of these places:

- tool capability -> `kimtools/<tool_name>`
- Dr. Yehoshua knowledge -> `intelligences/miu` and `BIFROST/MEMORY/MIU`
- behavior -> `kim_os/behavior`
- kernel/runtime -> `kim_os/kernel`
- temporary compatibility -> `kim_live/server.py`, with an extraction note

