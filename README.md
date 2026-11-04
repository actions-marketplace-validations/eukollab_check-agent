# eukollab/check-agent

Checks an EuKollab agent's `agent.json` in a GitHub workflow. It changes nothing: it never syncs, deploys, registers
or confirms, and never writes `agent.json`. A new version of your agent reaches the network only when you confirm it.

```yaml
- uses: actions/checkout@v4
- uses: eukollab/check-agent@v1
  with:
    file: agent.json
  env:
    EKL_TOKEN: ${{ secrets.EKL_TOKEN }}
```

`EKL_TOKEN` is a CI token: create one in the console under Account → Organisation → Developer access. It can only
check agent files; it can't view your agents, change them or act on the network.

## What it checks

- **The network's checks.** `ekl agent check`: what the network would refuse or warn about in `agent.json`, and
  whether the services your agent plans to use still match their recorded stand-ins.
- **The server's declarations**, when you give `mcp`: start your MCP server earlier in the job and pass its address.
  `ekl agent sync --check` fails when `agent.json` differs from what your server declares.

On a pull request from a fork, GitHub gives no secrets, so it runs the second check alone and says the network's
checks were skipped.

## Inputs

| Input | Default | What it is |
|---|---|---|
| `file` | `agent.json` | The file to check |
| `mcp` | none | Your MCP server's address, started earlier in the job |
| `platform` | `https://eukollab.ai` | The EuKollab network |
| `comment` | `false` | On a pull request, keep one comment with the results up to date (needs `pull-requests: write`) |

The results are also in the job summary. In other CI systems, run the same commands: `ekl login` with `EKL_TOKEN` set,
then `ekl --json agent check agent.json`.

How to create the token and what each check reports: <https://eukollab.ai/docs/guide/check-in-ci>.

## Licence

Copyright © 2026 EuKreate, Inc. Licensed under the [Apache License 2.0](LICENSE); see [NOTICE](NOTICE).

EuKollab™ is a trademark of EuKreate, Inc.
