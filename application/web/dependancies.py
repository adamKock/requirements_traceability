from fastapi import Request

def get_service(request: Request):
    return request.app.state.traceability_service