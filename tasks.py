import invoke


env = "default"


@invoke.task
def build(c):
    invoke.run(
        "poetry export -f requirements.txt --without-hashes --output ./src/requirements.txt"
    )
    invoke.run("black ./")
    invoke.run("sam validate")
    invoke.run("sam build -p")
    

@invoke.task(build)
def plan(c, env="default"):
    invoke.run(
        f"sam deploy --config-env {env} --no-execute-changeset --no-fail-on-empty-changeset"
    )


@invoke.task(build)
def deploy(c, env="default"):
    invoke.run(f"sam deploy --config-env {env} --no-fail-on-empty-changeset")


@invoke.task
def delete(c, env="default"):
    invoke.run(f"sam delete --config-env {env}")
