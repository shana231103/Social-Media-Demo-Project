from app.domain.models import BrowserCookie
from app.domain.repositories import BrowserCookieRepository
from app.application.dtos import SaveCookiesRequest

class SaveCookiesUseCase:
    def __init__(self, cookie_repo: BrowserCookieRepository):
        self.cookie_repo = cookie_repo

    def execute(self, request: SaveCookiesRequest) -> BrowserCookie:
        cookie = BrowserCookie(
            username=request.username,
            cookies=request.cookies,
            local_storage=request.local_storage
        )
        return self.cookie_repo.save(cookie)

class GetCookiesUseCase:
    def __init__(self, cookie_repo: BrowserCookieRepository):
        self.cookie_repo = cookie_repo

    def execute(self, username: str) -> BrowserCookie:
        cookie = self.cookie_repo.get_by_username(username)
        return cookie
