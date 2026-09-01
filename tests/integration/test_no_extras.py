"""Tests for the dependency-free core boundary."""

import subprocess
import sys
import types

import pytest

from betwixt import Betwixt, BetwixtError


@pytest.mark.absent_extra
def test_core_import_and_errors_are_dependency_free() -> None:
    """Import the core surface without requiring adapter packages."""
    assert issubclass(BetwixtError, Exception)
    assert Betwixt.__module__ == "betwixt.betwixt"


@pytest.mark.absent_extra
def test_optional_adapter_lookup_fails_in_an_extra_free_subprocess() -> None:
    """Verify optional declarations fail cleanly when both optional imports are blocked."""
    script = """
import builtins
from betwixt import Betwixt

real_import = builtins.__import__
def blocked(name, *args, **kwargs):
    if name == "pydantic" or name == "sqlalchemy":
        raise ImportError(name)
    return real_import(name, *args, **kwargs)
builtins.__import__ = blocked

class PydanticSide:
    pass
PydanticSide.__module__ = "pydantic.fake"
class SQLAlchemySide:
    __mapper__ = object()
SQLAlchemySide.__module__ = "sqlalchemy.fake"

for side in (PydanticSide, SQLAlchemySide):
    try:
        type("Mapping", (Betwixt,), {"left": side, "right": side})
    except Exception as error:
        assert "install betwixt[" in str(error).lower() or "adapter" in str(error).lower()
    else:
        raise AssertionError("optional declaration unexpectedly succeeded")
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


@pytest.mark.absent_extra
def test_user_defined_pydantic_subclass_detection_without_installing_pydantic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise Pydantic's user-defined subclass lookup with a dependency-free stand-in."""
    from betwixt.adapters.base import optional_adapter

    pydantic = types.ModuleType("pydantic")

    class BaseModel:
        pass

    pydantic.__dict__["BaseModel"] = BaseModel
    monkeypatch.setitem(sys.modules, "pydantic", pydantic)

    class UserModel(BaseModel):
        pass

    UserModel.__module__ = "application.models"

    adapter = optional_adapter(UserModel)
    assert adapter is not None
    assert adapter.type is UserModel
