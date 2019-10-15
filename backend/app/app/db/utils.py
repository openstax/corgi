from starlette.requests import Request


def get_db(request: Request):

    yield request.state.db

    request.state.db.remove()
