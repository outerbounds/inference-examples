# Usage guide for Outerbounds CLI to manage Deployments

The table below covers all the options available in the Outerbounds CLI for managing your Deployments. 

| Property                                  | CLI Flag                                  | Type            | CLI Override Allowed | Notes                               |
| ----------------------------------------- | ----------------------------------------- | --------------- | -------------------- | ----------------------------------- |
| **name**                                  | `--name <string>`                         | `string`        | Yes                  | **Required**                        |
| **port**                                  | `--port <integer>`                        | `integer`       | Yes                  | **Required**                        |
| **description**                           | `--description <string>`                  | `string`        | Yes                  |                                     |
| **image**                                 | `--image <string>`                        | `string`        | Yes                  |                                     |
| **tags**                                  | `--tag <string>` *(repeatable)*           | `string[]`      | Yes                  | e.g. `--tag team:ml --tag env:prod` |
| **secrets**                               | `--secret <string>` *(repeatable)*        | `string[]`      | Yes                  | The name of the secret created on the Outerbounds UI                                     |
| **compute\_pools**                        | `--compute-pools <string,...>`            | `string[]`      | Yes                  | Comma-separated list                |
| **environment**                           | `--env KEY=VALUE` *(repeatable)*          | `key=value`     | Yes                  | Complex values are JSON-ified       |
| **commands**                              | *no CLI override*                         | `string[]`      | No                   | Must live in config file            |
| **resources.cpu**                         | `--cpu <string>`                          | `string`        | Yes                  | e.g. `500m`, default `1`            |
| **resources.memory**                      | `--memory <string>`                       | `string`        | Yes                  | e.g. `4Gi`, default `4Gi`           |
| **resources.gpu**                         | `--gpu <string>`                          | `string`        | Yes                  |                                     |
| **resources.disk**                        | `--disk <string>`                         | `string`        | Yes                  | e.g. `20Gi`, default `20Gi`         |
| **auth.type**                             | `--auth-type <Browser\|API>`              | `string`        | Yes                  | default `Browser`                   |
| **replicas.fixed**                        | `--fixed-replicas <int>`                  | `integer`       | Yes                  | Disables autoscaling by setting a fixed number of replicas.                                    |
| **replicas.min**                          | `--min-replicas <int>`                    | `integer`       | Yes                  |                                     |
| **replicas.max**                          | `--max-replicas <int>`                    | `integer`       | Yes                  |                                     |
| **replicas.scaling\_policy.rpm**          | `--scaling-rpm <int>`                     | `integer`       | Yes                  | default `60`                        |
| **dependencies.from\_requirements\_file** | `--dep-from-requirements <path>`          | `string`        | No                   |                                     |
| **dependencies.from\_pyproject\_toml**    | `--dep-from-pyproject <path>`             | `string`        | No                   |                                     |
| **dependencies.python**                   | `--python <version>`                      | `string`        | No                   | e.g. `3.10`                         |
| **dependencies.pypi**                     | `--pypi <name>=<version>` *(repeatable)*  | `string=string` | No                   |                                     |
| **dependencies.conda**                    | `--conda <name>=<version>` *(repeatable)* | `string=string` | No                   |                                     |
| **package.src\_path**                     | `--package-src-path <path>`               | `string`        | Yes                  |                                     |
| **package.suffixes**                      | `--package-suffixes <.ext,...>`           | `string[]`      | Yes                  | Comma-separated                     |
| **no\_deps**                              | `--no-deps`                               | `boolean`       | Yes                  | Skips baking dependencies           |
| **force\_upgrade**                        | `--force-upgrade`                         | `boolean`       | Yes                  | Overwrites the configuration & code of the deployment regardless of whether another change is already in progress                                    |

# Config File 

Instead of specifying everything as a CLI argument when creating/updating the app, you can also define a `config.yaml` and provide the location to the config using `--config-file config.yaml` flag. 

For example, you can launch the same app without a config by doing: 

`outerbounds app deploy --name my-app port 8501 --min-replicas 0 --max-replicas 3 --scaling-rpm 100 --cpu 2 --memory 4Gi -- python main.py` 

Or, you can define a `config.yaml`: 

```
name: my-app 
port: 8501

replicas:
    min: 0
    max: 3
    scaling_policy:
        rpm: 100

resources:
    cpu: 2
    memory: 4Gi

commands:
- python main.py
```

and then invoke: 

`outerbounds app deploy --config-file config.yaml`. 