# REA integration bridge

Official project: https://github.com/morluto/rea
Official existing REA skill: https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything

## Decision rule

- **Ordinary Python/PyTorch source repository:** use search/read/AST/pytest, not REA. The REA project's own skill explicitly directs agents to skip REA for ordinary complete-source architecture analysis.
- **GGUF or safetensors model file:** use the REA `inspect_model_artifact` MCP tool when connected. It provides header/metadata/tensor declarations; it does not reverse a computational graph or learn training history from weights. Built-in `scripts/inspect_safetensors.py` is an offline fallback for safetensors only.
- **Compiled extension/native binary:** use REA's connected native-analysis tools, after checking provider readiness and authorization. Analyze smallest component related to the target function.
- **Packaged application/JavaScript/.NET/APK/browser behavior:** use the relevant REA capability only if this is central to the paper reproduction and source inspection is insufficient.
- **Unknown artifact format:** do not hand binary to REA blindly. Inventory file types and choose the tool shown in the connected MCP tool catalog.

## Available interface

If the REA MCP server is connected, enumerate exposed tools and follow **actual current tool schemas**. Do not assume availability from the presence of instructions alone. Capture returned evidence IDs, source locations, versions, unknowns, and limitations in `evidence.csv`.

If local `rea` CLI is already installed, examples from project docs include:

```bash
rea providers --json
rea capabilities --json
rea inspect-model-artifact /absolute/path/to/checkpoint.safetensors --json
```

Check `rea <command> --help` against the installed version before using extra flags. Do not automatically install, update, register or alter REA setup just because the skill was activated. If not connected, proceed using paper/source methods and record the unavailable capability.

If the user explicitly asks to set it up, current upstream setup has a review/approval step:

```bash
npx rea-agents@latest setup --client antigravity --dry-run --json
```

After the user reviews changes, they can apply supported setup through the upstream instructions. The MCP registration must be refreshed in the agent session if necessary. REA supports the Antigravity client ID, but the installed REA version may differ; verify current documentation.

## Evidence discipline

- An extracted string, tensor name, decompiled pseudocode or runtime trace is **observed** evidence; interpretation of the hidden high-level algorithm is **derived** or **hypothesis** until validated.
- Preserve artifact digest, tool version, command/tool name and limitations.
- Avoid inferring a training configuration from a checkpoint solely because names resemble conventional module names.
- Prefer the narrowest non-executing inspection; runtime execution may have side effects and requires informed authorization.
- Never use REA to bypass licensing, access controls or authorization.
