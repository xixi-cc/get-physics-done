---
name: gpd:set-profile
description: Switch research profile for GPD agents (deep-theory/numerical/exploratory/review/paper-writing)
argument-hint: <profile>
context_mode: projectless
allowed-tools:
  - file_read
  - file_write
  - shell
help:
  group: Configuration and maintenance
  order: 670
  compact_description: Switch the abstract model profile
  display_signature: gpd:set-profile <profile>
---


<objective>
Set the abstract `model_profile` to the requested supported profile. This maps
role tiers; it does not itself set reasoning effort, task counts or scientific
verification policy. Use `gpd:settings` for broader configuration and
`gpd:set-tier-models` for concrete runtime model IDs.
</objective>

<execution_context>
@{GPD_INSTALL_DIR}/workflows/set-profile.md
</execution_context>

<process>
This is an action command. Follow the included set-profile workflow exactly and execute its update step now; do not only describe the available profiles.
   </process>
