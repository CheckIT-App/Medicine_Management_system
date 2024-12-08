
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse

def create_http_exception_handler(templates,lang:str="en"):
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        _ = request.state._
        if exc.status_code == 401 or exc.status_code == 404:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "lang": lang,
                    "_":_,
                    "title": _("Unauthorized"),
                    "message": _("You must log in to access this page."),
                    "action_url": f"/{lang}/login",
                    "action_label": _("Login"),
                },
                status_code=exc.status_code,
            )
        elif exc.status_code == 403:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "lang": lang,
                    "title": _("Access Denied"),
                    "message": _("You do not have the necessary privileges to view this page."),
                    "action_url": f"/{lang}",
                    "action_label": _("Go Home"),
                },
                status_code=exc.status_code,
            )
        else:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "lang": lang,
                    "_": _,
                    "title": "Error",
                    "message": exc.detail,
                    "action_url": None,
                    "action_label": None,
                },
                status_code=exc.status_code,
        )
    return custom_http_exception_handler
