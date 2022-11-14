# Pulumi Databases

Quickly create databases in AWS. Helpful for testing.

## Usage

Select the dev stack.

```bash
pulumi stack select dev
```

Set your email address. This will be used in the AWS tags.

```bash
pulumi config set --path "tags.owner" "my.name@posit.co"
```

Select which databases you want to create.

```bash
pulumi config set --path "mariadb.create" true
pulumi config set --path "postgres.create" false
```

To see and edit all possible configuration values edit [Pulumi.dev.yaml](./Pulumi.dev.yaml).