from fastapi import Request

def get_traceability_service(request: Request):
    return request.app.state.traceability_service