import logging

from fastapi.responses import RedirectResponse


def get_server():
    from app.main import server

    return server


logger = logging.getLogger("uvicorn")


def patch_github_api():
    import app.github
    import app.github.api
    import tests.unit.init_test_data

    github_getters = [s for s in dir(app.github.api) if s.startswith("get_")]
    mock_map = []
    for getter in github_getters:
        mock_function = getattr(
            tests.unit.init_test_data, f"mock_{getter}", None
        )
        if mock_function is None:
            logger.warn(
                f"Missing mock function for {getter}. "
                "This is probably fine, but I thought you should know."
            )
        else:
            mock_map.append((getter, mock_function))

    for module in (app.github.api, app.github):
        for getter, mock_function in mock_map:
            setattr(module, getter, mock_function)


def disable_auth():
    import app.api.endpoints.auth
    import app.core.auth

    class MockOAuth:
        async def authorize_redirect(self, _, redirect_uri):
            return RedirectResponse(redirect_uri)

        async def authorize_access_token(self, *_):
            from uuid import uuid4

            return {"access_token": str(uuid4())}

    async def nop(*_args, **_kwargs):
        pass

    app.api.endpoints.auth.github_oauth = MockOAuth()
    app.api.endpoints.auth.sync_user_repositories = nop


patch_github_api()
disable_auth()

# Delay the loading of the server module until after everything is patched
server = get_server()
