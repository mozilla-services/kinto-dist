from typing import Callable, Tuple

import pytest
import requests
from kinto_http import AsyncClient, KintoException
from pytest import FixtureRequest
from requests.adapters import HTTPAdapter
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.util.retry import Retry


DEFAULT_SERVER = "http://localhost:8888/v1"
DEFAULT_AUTH = "user:pass"
DEFAULT_EDITOR_AUTH = "editor:pass"
DEFAULT_REVIEWER_AUTH = "reviewer:pass"
DEFAULT_BUCKET = "main-workspace"
DEFAULT_COLLECTION = "product-integrity"

Auth = Tuple[str, str]
ClientFactory = Callable[[Auth], AsyncClient]


def pytest_addoption(parser):
    parser.addoption(
        "--server",
        action="store",
        default=DEFAULT_SERVER,
        help="Kinto server (in form 'http(s)://<host>:<port>/v1')",
    )
    parser.addoption(
        "--auth",
        action="store",
        default=DEFAULT_AUTH,
        help="Basic authentication",
    )
    parser.addoption(
        "--editor-auth",
        action="store",
        default=DEFAULT_EDITOR_AUTH,
        help="Basic authentication for editor",
    )
    parser.addoption(
        "--reviewer-auth",
        action="store",
        default=DEFAULT_REVIEWER_AUTH,
        help="Basic authentication for reviewer",
    )
    parser.addoption(
        "--bucket",
        action="store",
        default=DEFAULT_BUCKET,
        help="Source bucket",
    )
    parser.addoption(
        "--collection",
        action="store",
        default=DEFAULT_COLLECTION,
        help="Source collection",
    )
    parser.addoption(
        "--keep-existing",
        action="store_true",
        default=False,
        help="Keep existing collection data",
    )


@pytest.fixture(scope="session")
def server(request) -> str:
    return request.config.getoption("--server")


@pytest.fixture(scope="session")
def auth(request) -> Auth:
    return tuple(request.config.getoption("--auth").split(":"))


@pytest.fixture(scope="session")
def editor_auth(request) -> Auth:
    return tuple(request.config.getoption("--editor-auth").split(":"))


@pytest.fixture(scope="session")
def reviewer_auth(request) -> Auth:
    return tuple(request.config.getoption("--reviewer-auth").split(":"))


@pytest.fixture(scope="session")
def source_bucket(request) -> str:
    return request.config.getoption("--bucket")


@pytest.fixture(scope="session")
def source_collection(request) -> str:
    return request.config.getoption("--collection")


@pytest.fixture(scope="session")
def keep_existing(request) -> bool:
    return request.config.getoption("--keep-existing")


@pytest.fixture
def make_client(
    server: str, source_bucket: str, source_collection: str
) -> ClientFactory:
    """Factory as fixture for creating a Kinto AsyncClient used for tests.

    Args:
        server (str): Kinto server (in form 'http(s)://<host>:<port>/v1')
        source_bucket (str): Source bucket
        source_collection (str): Source collection

    Returns:
        AsyncClient: AsyncClient
    """

    def _make_client(auth: Auth) -> AsyncClient:
        request_session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        request_session.mount(
            f"{server.split('://')[0]}://", HTTPAdapter(max_retries=retries)
        )

        create_user(request_session, server, auth)

        return AsyncClient(
            server_url=server,
            auth=auth,
            bucket=source_bucket,
            collection=source_collection,
            retry=5,
        )

    return _make_client


@pytest.fixture(autouse=True)
async def flush_default_collection(
    make_client: ClientFactory,
    auth: Auth,
    source_bucket: str,
    source_collection: str,
):
    yield
    client = make_client(auth)

    try:
        await client.delete_collection(
            id=source_collection, bucket=source_bucket, if_exists=True
        )
    except KintoException as e:
        # in the case where a user doesn't have permissions to delete
        print(e)


@pytest.fixture(scope="session", autouse=True)
def verify_url(request: FixtureRequest, base_url: str):
    """Verifies the base URL"""
    verify = request.config.option.verify_base_url
    if base_url and verify:
        session = requests.Session()
        retries = Retry(backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        session.mount(base_url, HTTPAdapter(max_retries=retries))
        session.get(base_url, verify=False)


@pytest.fixture
def firefox_options(firefox_options: Options) -> Options:
    firefox_options.headless = True
    return firefox_options


@pytest.fixture
def selenium(selenium: WebDriver) -> WebDriver:
    selenium.set_window_size(1024, 600)
    selenium.maximize_window()
    selenium.implicitly_wait(5)
    return selenium


def create_user(request_session: requests.Session, server: str, auth: Auth):
    # check if user already exists before creating
    r = request_session.get(server, auth=auth)
    if "user" not in r.json():
        assert request_session.put(
            f"{server}/accounts/{auth[0]}",
            json={"data": {"password": auth[1]}},
        )
