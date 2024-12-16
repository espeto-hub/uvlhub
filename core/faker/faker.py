from exrex import getone
from faker.providers import BaseProvider


class RegexProvider(BaseProvider):
    def regex(self, pattern: str) -> str:
        return getone(pattern)
