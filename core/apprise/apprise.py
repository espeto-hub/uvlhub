from apprise import Apprise

class AppriseExtension:
    def __init__(self, app=None):
        self.apprise = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.apprise = Apprise()

    def add(self, *args, **kwargs):
        self.apprise.add(*args, **kwargs)

    def notify(self, *args, **kwargs):
        return self.apprise.notify(*args, **kwargs)

    def len(self, *args, **kwargs):
        return self.apprise.len(*args, **kwargs)

    def clear(self, *args, **kwargs):
        return self.apprise.clear(*args, **kwargs)

    def details(self, *args, **kwargs):
        return self.apprise.details(*args, **kwargs)

    async def async_notify(self, *args, **kwargs):
        return await self.apprise.async_notify(*args, **kwargs)

    @property
    def service_names(self):
        return sorted([str(s['service_name']) for s in self.details()['schemas']])
