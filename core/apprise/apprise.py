import os
import re

import apprise
from apprise import Apprise
from apprise.asset import AppriseAsset
from faker import Faker

from core.faker.faker import RegexProvider


class AppriseExtension:
    def __init__(self, app=None):
        self.apprise = None
        if app is not None:
            self.init_app(app)
        self.faker = Faker()
        self.faker.add_provider(RegexProvider)

    def init_app(self, app):
        self.apprise = Apprise(asset=AppriseAsset(
            app_id='UVLHub',
            app_desc='UVLHub',
            app_url='https://uvlhub.tail729c.ts.net/',
            image_path_mask=os.path.join(os.getenv('WORKING_DIR', ''), 'app', 'static', 'img', 'icons',
                                         'icon-{XY}.{EXTENSION}')
        ))

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
        return sorted(
            [str(s['service_name']) for s in self.details()['schemas'] if self.get_service_schema(s['service_name'])])

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
                            # determine which delimiter is being used from the token_details['delim'] tuple
                            # and split the value on that delimiter
                            used_delim = None
                            for delim in token_details['delim']:
                                if delim in value:
                                    used_delim = delim
                                    break
                            if used_delim is None:
                                if token_details.get('regex') is not None and not re.match(token_details['regex'][0],
                                                                                           value):
                                    return None, f'Invalid list:string value for {token_details["name"]}, must match regular expression {token_details["regex"][0]}'
                            else:
                                values = value.split(used_delim)
                                for v in values:
                                    if token_details.get('regex') is not None and not re.match(
                                            token_details['regex'][0], v):
                                        return None, f'Invalid list:string value for {token_details["name"]}, must match regular expression {token_details["regex"][0]}'
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

    def send_message(self, urls, **kwargs):
        self.add(urls)
        result = self.notify(**kwargs)
        self.clear()
        return result

    def generate_url_example(self, service_name):
        service = self.get_service_schema(service_name)
        if service is None:
            return f'{service_name} is not a valid service'

        service_details = service['details']
        example = self.faker.random_element(service_details['templates'])
        for token, details in service_details['tokens'].items():
            match details["type"]:
                case 'int':
                    example = example.replace(f'{{{token}}}', str(self.faker.random_int(min=details.get('min', 0),
                                                                                        max=details.get('max', 100))))
                case 'float':
                    example = example.replace(f'{{{token}}}', str(self.faker.pyfloat(min_value=details.get('min', 0.0),
                                                                                     max_value=details.get('max',
                                                                                                           100.0))))
                case 'string':
                    if details.get('regex') is not None:
                        example = example.replace(f'{{{token}}}', self.faker.regex(details['regex'][0]))
                    else:
                        example = example.replace(f'{{{token}}}', self.faker.pystr(min_chars=5, max_chars=20))
                case 'bool':
                    example = example.replace(f'{{{token}}}', self.faker.random_element(['true', 'false']))
                case 'list:int':
                    delimiter = self.faker.random_element(details.get('delim', [',']))
                    example = example.replace(f'{{{token}}}', delimiter.join(
                        str(self.faker.random_int(min=details.get('min', 0), max=details.get('max', 100))) for _ in
                        range(self.faker.random_int(min=1, max=3))))
                case 'list:float':
                    delimiter = self.faker.random_element(details.get('delim', [',']))
                    example = example.replace(f'{{{token}}}', delimiter.join(
                        str(self.faker.pyfloat(min_value=details.get('min', 0.0), max_value=details.get('max', 100.0)))
                        for
                        _ in range(self.faker.random_int(min=1, max=3))))
                case 'list:string':
                    delimiter = self.faker.random_element(details.get('delim', [',']))
                    if details.get('regex') is not None:
                        example = example.replace(f'{{{token}}}', delimiter.join(
                            self.faker.regex(details['regex'][0]) for _ in range(self.faker.random_int(min=1, max=3))))
                    else:
                        example = example.replace(f'{{{token}}}', delimiter.join(
                            self.faker.pystr(min_chars=5, max_chars=20) for _ in
                            range(self.faker.random_int(min=1, max=3)))
                                                  )
                case t if 'choice:' in t:
                    example = example.replace(f'{{{token}}}', self.faker.random_element(details['values']))
        return example

    def html_guide(self, service_name):
        service = self.get_service_schema(service_name)
        if service is None:
            return f'{service_name} has no documentation available'

        service_details = service['details']
        html = f'<h1 class="card-title">{service_name}</h1>'
        html += '<h2>Templates</h2>'
        html += '<ul>'
        for schema in service_details['tokens']['schema']['values']:
            for template in service_details['templates']:
                html += f'<li>{template.replace('{schema}', schema)}</li>'
        html += '</ul>'
        html += '<h2>Tokens</h2>'
        html += '<table class="table">'
        html += '<tr><th>Token</th><th>Required</th><th>Type</th><th>Constraints</th></tr>'
        for token, details in sorted(service_details['tokens'].items(),
                                     key=lambda x: (not x[1]['required'], x[1]['name'])):
            if token == 'schema':
                continue
            html += f'<tr><td>{details["name"]}</td>'
            html += f'<td>{"Yes" if details["required"] else "No"}</td>'
            match details["type"]:
                case 'int':
                    html += f'<td>Integer</td>'
                case 'float':
                    html += f'<td>Float</td>'
                case 'string':
                    html += f'<td>String</td>'
                case 'list:int':
                    html += f'<td>List of integers</td>'
                case 'list:float':
                    html += f'<td>List of floats</td>'
                case 'list:string':
                    html += f'<td>List of strings</td>'
                case t if 'choice:' in t or 'bool' in t:
                    html += f'<td>Choice</td>'
            constraints = []
            if details.get('min') is not None:
                constraints.append(f'<strong>Min:</strong> {details["min"]}')
            if details.get('max') is not None:
                constraints.append(f'<strong>Max:</strong> {details["max"]}')
            if details.get('values') is not None:
                constraints.append(f'<strong>Allowed values:</strong> {", ".join(details["values"])}')
            if details.get('regex') is not None:
                constraints.append(f'<strong>Regex:</strong> {details["regex"][0]}')
            html += f'<td>{"<br>".join(constraints) if constraints else "-"}</td></tr>'
        html += '</table>'
        html += '<h2>Examples</h2>'
        html += '<ul>'
        for _ in range(3):
            html += f'<li>{self.generate_url_example(service_name)}</li>'
        html += '</ul>'
        html += '<h2>Information</h2>'
        html += f"<p>For obtaining the required tokens, visit the <a href='{service["service_url"]}' target='_blank'>service's page</a>.<br>For more parameters and examples, visit the <a href='{service["setup_url"]}' target='_blank'>documentation</a>.</p>"
        return html
