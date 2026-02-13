from compose.gunicorn.settings import GunicornSettings, export_settings


class SampleSettings(GunicornSettings):
    wsgi_app: str = "test.app:app"
    workers: int = 1
    threads: int = 2
    timeout: int = 60


def test_export_settings():
    globals_ = {}

    export_settings(globals_, SampleSettings())

    assert globals_["wsgi_app"] == "test.app:app"
    assert globals_["workers"] == 1
    assert globals_["timeout"] == 60


def test_export_with_kwargs_override():
    globals_ = {}

    export_settings(globals_, SampleSettings(), accesslog="-")

    assert globals_["accesslog"] == "-"
    assert globals_["wsgi_app"] == "test.app:app"


def test_export_with_env_override():
    globals_ = {}

    export_settings(
        globals_,
        SampleSettings(),
        env="prd",
        overrides={"prd": {"workers": 3}},
    )

    assert globals_["workers"] == 3
    assert globals_["timeout"] == 60


def test_export_with_env_not_in_overrides_use_default():
    globals_ = {}

    export_settings(
        globals_,
        SampleSettings(),
        env="stg",
        overrides={"prd": {"workers": 3}},
    )

    assert globals_["workers"] == 1


def test_export_with_env_none_ignore_overrides():
    globals_ = {}

    export_settings(
        globals_,
        SampleSettings(),
        env=None,
        overrides={"prd": {"workers": 3}},
    )

    assert globals_["workers"] == 1


def test_export_with_env_and_kwargs():
    globals_ = {}

    export_settings(
        globals_,
        SampleSettings(),
        env="prd",
        overrides={"prd": {"workers": 3}},
        accesslog="-",
    )

    assert globals_["workers"] == 3
    assert globals_["accesslog"] == "-"
