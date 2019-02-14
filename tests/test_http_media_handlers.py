import json

import pytest

from bocadillo import API
from bocadillo.constants import CONTENT_TYPE
from bocadillo.media import UnsupportedMediaType


def test_defaults_to_json(api: API):
    data = {"message": "hello"}

    @api.route("/")
    async def index(req, res):
        res.media = data

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == data


def test_can_specify_media_type_when_creating_the_api_object():
    API(media_type=CONTENT_TYPE.JSON)


def test_media_type_is_accessible_on_api(api: API):
    assert hasattr(api, "media_type")


@pytest.mark.parametrize(
    "media_type, expected_text", [(CONTENT_TYPE.JSON, json.dumps)]
)
def test_use_builtin_media_handlers(api: API, media_type: str, expected_text):
    api.media_type = media_type
    data = {"message": "hello"}

    @api.route("/")
    async def index(req, res):
        res.media = data

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == media_type
    assert response.text == expected_text(data)


@pytest.fixture
def foo_type():
    return "application/foo"


@pytest.fixture
def handle_foo():
    return lambda value: f"FOO: {value}"


def test_add_and_use_custom_media_handler(api: API, foo_type, handle_foo):
    api.media_handlers[foo_type] = handle_foo
    api.media_type = foo_type

    @api.route("/")
    async def index(req, res):
        res.media = "bar"

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == foo_type
    assert response.text == handle_foo("bar")


def test_replace_media_handlers(api: API, foo_type, handle_foo):
    api.media_handlers = {foo_type: handle_foo}
    api.media_type = foo_type

    @api.route("/")
    async def index(req, res):
        res.media = "bar"

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == foo_type
    assert response.text == handle_foo("bar")


def test_if_media_type_not_supported_then_passing_it_raises_error(
    api: API, foo_type
):
    with pytest.raises(UnsupportedMediaType) as ctx:
        API(media_type=foo_type)

    assert foo_type in str(ctx.value)


def test_if_media_type_not_supported_then_setting_it_raises_error(
    api: API, foo_type
):
    with pytest.raises(UnsupportedMediaType) as ctx:
        api.media_type = foo_type

    assert foo_type in str(ctx.value)
