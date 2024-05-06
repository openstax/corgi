import pytest

from app.core.auth import RequiresRole
from app.data_models.models import Role, UserSession


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "user_role,required_role,message",
    [
        (Role.DEFAULT, Role.ADMIN, "Lesser roles should not be allowed"),
        (Role.USER, Role.ADMIN, "Lesser roles should not be allowed"),
    ],
)
def test_requires_role_errors_for_lesser_role(
    user_role, required_role, message
):
    from fastapi import HTTPException

    user = UserSession(id=1, token="", role=user_role, avatar_url="/", name="")
    with pytest.raises(HTTPException) as httpex:
        RequiresRole(required_role)(user)
        exc = httpex.value
        assert exc.status_code == 403, message


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "user_role,required_role,message",
    [
        (Role.ADMIN, Role.ADMIN, "Equal roles should be allowed"),
        (Role.ADMIN, Role.USER, "Greater roles should be allowed"),
    ],
)
def test_requires_role_succeeds_for_correct_role(
    user_role, required_role, message
):
    user = UserSession(id=1, token="", role=user_role, avatar_url="/", name="")
    exc = None
    try:
        RequiresRole(required_role)(user)
    except Exception as e:
        exc = e
    assert exc is None, message
