import os
import tempfile
import pathlib
import tarfile
import yaml
import json
import re
import base64
import secrets
import asyncio
import random

import click
import httpx
from pydantic import BaseModel, validator

ENTRYPOINT_FORMAT = re.compile(r"^[A-z][A-z0-9\_\.]*:[A-z][A-z0-9\_]*$")

COCOHUB_SUBMIT_URL = "https://cocohub.ai/v2/submit_puppet_app"
COCOHUB_TOKEN_URL = "https://cocohub.ai/v2/service_account/token"
COCOHUB_AUTHORIZE_SERVICE_ACCOUNT_URL = "https://cocohub.ai/auth/confirm_service_account"

SERVICE_ACCOUNT_PATH = os.environ.get("PUPPET_SERVICE_ACCOUNT", "~/.puppet_service_account")

class ComponentYAML(BaseModel):
    component_id: str
    entrypoint: str

    @validator("entrypoint")
    def entrypoint_format(cls, v):
        if not ENTRYPOINT_FORMAT.match(v):
            raise ValueError("entrypoint format should be module_name.module_name:puppet_component_func")
        return v

class CoCoHubServiceAccount(BaseModel):
    client_id: str
    client_secret: str
    name: str = ""

def validate_project(component_yaml_path):
    with open(component_yaml_path, "r") as f:
        project_config = ComponentYAML.validate(yaml.safe_load(f))
    return project_config

def package_project(tmpdir: pathlib.Path, component_id: str):
    project_root = pathlib.Path(".")
    (project_root / "requirements.txt").touch()
    project_tar_file = tmpdir / f"{component_id}.tar.gz" 
    with tarfile.open(project_tar_file, "w:gz") as tar:
        for f in project_root.glob("*"):
            tar.add(f, recursive=True)
    return project_tar_file

def generate_service_account(service_account_path):
    service_account = CoCoHubServiceAccount(
        name=os.uname().nodename,
        client_id=secrets.token_urlsafe(12),
        client_secret=secrets.token_urlsafe(24)
    )
    with service_account_path.open("w") as f:
        json.dump(service_account.dict(), f, indent=True)

    with service_account_path.open("r") as f:
        base64_service_account = base64.b64encode(f.read().encode("utf-8")).decode("utf-8")
    
    import webbrowser
    webbrowser.open(COCOHUB_AUTHORIZE_SERVICE_ACCOUNT_URL + f"?serviceAccount={base64_service_account}")
    if not click.confirm("Are you done authenticating at CoCoHub?"):
        service_account_path.unlink()
        raise Exception("No service account. try again after authenticating at CoCoHub")
    return service_account

async def get_access_token(http_client):
    service_account_path = pathlib.Path(os.path.expanduser(SERVICE_ACCOUNT_PATH))
    if service_account_path.exists():
        with service_account_path.open("r") as f:
            service_account: CoCoHubServiceAccount = CoCoHubServiceAccount.validate(json.load(f))
    else:
        if click.confirm("No service account. do you want to generate one now?"):
            service_account = generate_service_account(service_account_path)
        else:
            raise Exception("No service account. try again after authenticating at CoCoHub")

    http_response = await http_client.post(
        COCOHUB_TOKEN_URL,
        auth=(service_account.client_id, service_account.client_secret),
        headers={"content-length": "0"}
        )
    http_response.raise_for_status()
    access_token = http_response.json()
    return access_token

async def push_deployment(http_client, project_tarfile, access_token):
    files = {'file': project_tarfile.open("rb")}
    headers = {"Authorization": f"Bearer {access_token['access_token']}"}
    http_response = await http_client.post(COCOHUB_SUBMIT_URL, files=files, headers=headers, timeout=60*5)
    http_response.raise_for_status()
    return http_response.json()

async def deploy(project_config_path):
    async with httpx.AsyncClient() as http_client:
        with tempfile.TemporaryDirectory() as tmpdir_p:
            click.echo("Authenticating..")
            access_token = await get_access_token(http_client)

            tmpdir = pathlib.Path(tmpdir_p)
            proj_conf = validate_project(project_config_path)

            if click.confirm(f'Deploying {proj_conf.component_id}, Do you want to continue?'):

                tarfile = package_project(tmpdir, proj_conf.component_id)
                deploy_task = asyncio.create_task(push_deployment(http_client, tarfile, access_token))
                print()
                random_signs = ["⭐️", "💫", "🌟", "✨", "⚡️"]
                while not deploy_task.done():
                    random_sign = random.choice(random_signs)
                    print(f"\r{random_sign} Deploying... {random_sign}", end="")
                    await asyncio.sleep(1)
                print("\nDone! 🔥")
                print(f"Component available at: {deploy_task.result()['cocohub_url']}")