<purpose>
Switch the research mode profile used by GPD agents. Controls agent behavior, emphasis, and model selection for different phases of physics research work.
</purpose>

<required_reading>
Read all files referenced by the invoking prompt's execution_context before starting.
</required_reading>

<process>

This is an action workflow. Execute the validation and update steps; do not only explain profile options or summarize the selected mode.

<step name="validate">
Parse and validate the raw single profile argument:

```bash
PROFILE="$(printf '%s' "$ARGUMENTS" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
case "$PROFILE" in
  deep-theory|numerical|exploratory|review|paper-writing) ;;
  "")
    echo "ERROR: Missing profile. Valid profiles: deep-theory, numerical, exploratory, review, paper-writing"
    exit 1
    ;;
  *[[:space:]]*)
    echo "ERROR: set-profile accepts exactly one profile argument."
    exit 1
    ;;
  *)
    echo "ERROR: Invalid profile \"$PROFILE\". Valid profiles: deep-theory, numerical, exploratory, review, paper-writing"
    exit 1
    ;;
esac
```

</step>

<step name="ensure_and_load_config">
Ensure config exists without initializing or mutating project state:

```bash
gpd config ensure-section
```

This creates or repairs the config section only. Do not run `gpd init`, `gpd progress`, state sync, or project reentry from `set-profile`; this command is allowed to change only `GPD/config.json::model_profile`.
</step>

<step name="update_config">
Update only the `model_profile` field through the config CLI, preserving all other `GPD/config.json` keys:

```bash
gpd config set model_profile "$PROFILE"
```
</step>

<step name="confirm">
Display confirmation with profile details for selected profile:

```
Profile set to: $PROFILE

Agents will now operate in this mode:

[Show profile details for selected profile]
```

**Profile definitions:**

Canonical per-agent tier assignments live in `MODEL_PROFILES` and the installed reference `references/orchestration/model-profiles.md`; the profiles cover assignments across all 20 agents. Do not copy the agent/tier matrix here; use that reference when exact tier rows are needed.

The profile maps abstract role tiers for deep-theory, numerical, exploratory,
review or paper-writing work. It does not itself change task counts, research
mode, review cadence, proof requirements or the current model's reasoning effort.
Report the actual selected profile; read the canonical matrix only when exact
agent/tier assignments are requested.

</step>

</process>

<success_criteria>
- [ ] Argument validated against five physics research profiles
- [ ] Config file ensured
- [ ] Config updated with new model_profile
- [ ] Confirmation displayed with profile details including model assignments and behavioral emphasis
</success_criteria>
