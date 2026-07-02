# Kim Module Contract

Every Kim module must declare:

1. `id`
2. `type`: kernel | behavior | intelligence | knowledge | tool | external_library
3. `owner`
4. `source_of_truth`
5. `runtime_entrypoint`
6. `inputs`
7. `outputs`
8. `success_contract`
9. `confirmation_policy`
10. `memory_policy`

## Module Types

### Kernel

Runs Kim. Does not contain domain truth.

### Behavior

Defines tone, service posture and escalation.

### Intelligence

Loaded human/company intelligence, such as MIU.

### Knowledge

Indexed facts, preferences, doctrine and learned context.

### Tool

Executes actions with verifiable result.

### External Library

Read-only or reference material from outside the loaded intelligence.

