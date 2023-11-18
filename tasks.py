import invoke


env = "default"


@invoke.task
def build(c):
    invoke.run(
        "poetry export -f requirements.txt --with test_distribution --without-hashes --output ./functions/test_distribution/requirements.txt"
    )
    invoke.run("black functions")
    invoke.run("sam validate --lint")
    invoke.run("sam build --parallel")


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
