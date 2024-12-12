import re

import apprise
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

    def get_service_schema(self, service_name):
        return next((s for s in self.details()['schemas'] if s['service_name'] == service_name), None)

    def is_url_valid(self, url, service_name):
        service_details = self.get_service_schema(service_name)
        if service_details is None:
            return None, f'{service_name} is not a valid service'
        else:
            service_details = service_details['details']

        for template in service_details['templates']:
            regex = re.compile(fr'^{re.sub(r'\{([^{}]+)\}', r'(?P<\1>[^:/]+)', template)}$')
            match = regex.match(url)
            if match:
                for token, value in match.groupdict().items():
                    token_details = service_details['tokens'].get(token)
                    if token_details is None:
                        return None, f'URL does not match template {template}'
                    if token_details.get('alias_of'):
                        token_details = service_details['tokens'][token_details['alias_of']]

                    match token_details['type']:
                        case 'int':
                            if not value.isdigit():
                                return None, f'Invalid integer for {token_details["name"]}'
                            if token_details.get('min') is not None and int(value) < token_details['min']:
                                return None, f'{token_details["name"]} must be greater than or equal to {token_details["min"]}'
                            if token_details.get('max') is not None and int(value) > token_details['max']:
                                return None, f'{token_details["name"]} must be less than or equal to {token_details["max"]}'
                        case 'float':
                            if not re.match(r'^\d+(\.\d+)?$', value):
                                return None, f'Invalid float for {token_details["name"]}'
                            if token_details.get('min') is not None and float(value) < token_details['min']:
                                return None, f'{token_details["name"]} must be greater than or equal to {token_details["min"]}'
                            if token_details.get('max') is not None and float(value) > token_details['max']:
                                return None, f'{token_details["name"]} must be less than or equal to {token_details["max"]}'
                        case 'string':
                            if token_details.get('regex') is not None and not re.match(token_details['regex'][0],
                                                                                       value):
                                return None, f'Invalid string for {token_details["name"]}, must match regular expression {token_details["regex"][0]}'
                        case 'list:int':
                            continue
                        case 'list:float':
                            continue
                        case 'list:string':
                            continue
                        case t if 'choice:' in t or 'bool' in t:
                            if value not in token_details['values']:
                                return None, f'Invalid choice for {token_details["name"]}, must be one of: {", ".join(token_details["values"])}'
                        case _:
                            return None, f'Unknown token type {token_details["type"]}'
                return True, None
            return None, 'URL does not match any template'

    def send_test_message(self, urls: str | list[str]):
        self.add(urls)
        with apprise.LogCapture(level=apprise.logging.INFO) as logs:
            result = self.notify(title='Test Notification', body='This is a test notification')
            message = logs.getvalue()
        self.clear()
        message = ' - '.join(message.replace('\n', '').split(' - ')[2:])
        return result, message
