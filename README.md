# KimOne

Last updated: 2026-07-02

KimOne is the GitHub/source home for Kim Live and the BIFROST agent workbench.

## Current Source

```text
/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne
```

Current branch:

```text
bifrost/kim-live-initial
```

Current backend version in `kim_live/server.py`:

```text
1.5.70
```

## Contents

- `kim_os/`: modular operating-system layer for kernel, behavior, knowledge routing and module contracts.
- `intelligences/miu/`: MIU (`μ`), Dr. Yehoshua's loaded intelligence package.
- `kimtools/`: executable tools with contracts and success evidence.
- `kim_live/`: current local Kim Live frontend/backend source.
- `kim_live/API_BRIDGE.md`: current bridge capability spec and change history.
- `kim_live/context/portfolio_report_overrides.json`: portfolio/reporting
  override state used by Kim Live.
- `.gitignore`: excludes local secrets, runtime logs, caches and temporary
  files.

## Operating Rule

New work should land in the right layer:

- runtime/kernel -> `kim_os/kernel`
- behavior prompt -> `kim_os/behavior`
- loaded intelligence -> `intelligences/miu`
- durable knowledge -> `BIFROST/MEMORY/MIU` or `BIFROST/KNOWLEDGE/MIU`
- executable capability -> `kimtools/<tool>`
- compatibility glue -> `kim_live/server.py`

`kim_live/server.py` is a legacy monolith during migration, not the long-term architecture.

Edit source here first, compile, then deploy to runtime:

```bash
cd /Users/dryehoshuapython/Documents/BIFROST/repos/KimOne
python3 -m py_compile kim_live/server.py kim_live/twilio_realtime_bridge.py
cp kim_live/server.py /Users/dryehoshuapython/.kim_live/server.py
cp kim_live/twilio_realtime_bridge.py /Users/dryehoshuapython/.kim_live/twilio_realtime_bridge.py
launchctl kickstart -k gui/$(id -u)/com.codex.kim.live
```

Use targeted copies for docs/assets/config as needed. Do not rely on
runtime-only edits.

## Current Local Git State

As of 2026-06-07, this local branch is synced with GitHub through:

```
3e6f184 Update BIFROST documentation handoff
```

Remote uses SSH: `git@github.com:dryehoshua/KimOne.git`.

## Secrets

Secrets are stored in macOS Keychain, not in this repository. Do not commit API
keys, tokens, passwords, PINs, voice phrases or OAuth client secrets.
