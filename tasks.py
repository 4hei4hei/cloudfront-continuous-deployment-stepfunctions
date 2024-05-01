import invoke


env = "default"


@invoke.task
def validate(c):
    invoke.run("black functions")
    invoke.run("flake8 functions --max-line-length=120")
    invoke.run("sam validate --lint")
    invoke.run("cfn-lint --template template.yaml")


@invoke.task
def up(c):
    invoke.run(f"docker compose up -d")


@invoke.task
def down(c):
    invoke.run(f"docker compose down")


@invoke.task(validate)
def build(c):
    invoke.run(
        "poetry export -f requirements.txt --with test_distribution --without-hashes --output ./functions/test_distribution/requirements.txt"
    )
    invoke.run("sam build --parallel --use-container")


@invoke.task(build)
def test(c):
    invoke.run(f"pytest -v")


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
