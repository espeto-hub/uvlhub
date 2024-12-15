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
        self.apprise = Apprise(
            asset=AppriseAsset(
                app_id='UVLHub',
                app_desc='UVLHub',
                app_url='https://uvlhub.tail729c.ts.net/',
                image_path_mask=os.path.join(
                    os.getenv('WORKING_DIR', ''), 'app', 'static', 'img', 'icons', 'icon-{XY}.{EXTENSION}'
                ),
            )
        )

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
        service_names = []
        for schema in self.details()['schemas']:
            if schema.get('service_name') and schema.get('details'):
                if schema['details'].get('templates') and schema['details'].get('tokens'):
                    service_names.append(str(schema['service_name']))
        return sorted(service_names)

    def get_service_schema(self, service_name):
        for name in self.service_names:
            if name == service_name:
                schema = [schema for schema in self.details()['schemas'] if str(schema['service_name']) == service_name]
                if schema:
                    return schema[0]
        return None

    def get_service_templates(self, service_name):
        service = self.get_service_schema(service_name)
        if service is None:
            return []
        return service['details']['templates']

    def is_url_valid(self, url, service_name):
        if url == 'test://test/test':
            return True, None
        service_details = self.get_service_schema(service_name)
        if service_details is None:
            return True, None
        else:
            service_details = service_details['details']
        template_matches = {}
        for template in service_details['templates']:
            template_matches[template] = {'match': False, 'errors': []}
            regex = re.compile(fr'^{re.sub(r"\{([^{}]+?)}", r"(?P<\1>[^{}]+?)", template)}$')
            template_matches[template]['regex'] = regex.pattern
            match = regex.match(url)
            if match:
                template_matches[template]['match'] = True
                template_matches[template]['errors'] = []
                try:
                    for token, value in match.groupdict().items():
                        token_details = service_details['tokens'].get(token)
                        if token_details.get('alias_of'):
                            token_details = service_details['tokens'][token_details['alias_of']]

                        match token_details['type']:
                            case 'int':
                                if not value.isdigit():
                                    template_matches[template]['errors'].append(
                                        f'Invalid integer for {token_details["name"]}'
                                    )
                                if token_details.get('min') is not None and int(value) < token_details['min']:
                                    template_matches[template]['errors'].append(
                                        f'{token_details["name"]} must be greater than'
                                        f' or equal to {token_details["min"]}'
                                    )
                                if token_details.get('max') is not None and int(value) > token_details['max']:
                                    template_matches[template]['errors'].append(
                                        f'{token_details["name"]} must be less than or equal to {token_details["max"]}'
                                    )
                            case 'float':
                                if not re.match(r'^\d+(\.\d+)?$', value):
                                    template_matches[template]['errors'].append(
                                        f'Invalid float for {token_details["name"]}'
                                    )
                                if token_details.get('min') is not None and float(value) < token_details['min']:
                                    template_matches[template]['errors'].append(
                                        f'{token_details["name"]} must be greater than'
                                        f' or equal to {token_details["min"]}'
                                    )
                                if token_details.get('max') is not None and float(value) > token_details['max']:
                                    template_matches[template]['errors'].append(
                                        f'{token_details["name"]} must be less than or equal to {token_details["max"]}'
                                    )
                            case 'string':
                                if token_details.get('regex') is not None:
                                    try:
                                        if not re.match(token_details['regex'][0], value):
                                            template_matches[template]['errors'].append(
                                                f'Invalid string for {token_details["name"]},'
                                                f' must match regular expression {token_details["regex"][0]},'
                                                f' got {value}'
                                            )
                                    except re.error:
                                        continue
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
                                    values = [value]
                                else:
                                    values = value.split(used_delim)

                                for v in values:
                                    if token_details.get('group'):
                                        regex_errors = []
                                        for group_token in token_details.get('group'):
                                            group_token_details = service_details['tokens'][group_token]
                                            if group_token_details.get('alias_of'):
                                                group_token_details = service_details['tokens'][
                                                    group_token_details['alias_of']
                                                ]

                                            if group_token_details.get('regex'):
                                                try:
                                                    if not re.match(group_token_details['regex'][0], v):
                                                        regex_errors.append(group_token_details["regex"][0])
                                                    else:
                                                        regex_errors.append(None)
                                                except re.error:
                                                    pass
                                            else:
                                                regex_errors.append(None)
                                        if None not in regex_errors:
                                            regex_errors = [x for x in regex_errors if x is not None]
                                            template_matches[template]['errors'].append(
                                                f'Invalid list:string value for {token_details["name"]}'
                                                f' on {values.index(v)}º element,'
                                                ' must match one of these regular expressions:'
                                                f' {", ".join(regex_errors)},'
                                                f' got {v}'
                                            )
                                    else:
                                        if token_details.get('regex'):
                                            try:
                                                if not re.match(token_details['regex'][0], v):
                                                    template_matches[template]['errors'].append(
                                                        f'Invalid list:string value for {token_details["name"]}'
                                                        f' on {values.index(v)}º element,'
                                                        f' must match regular expression {token_details["regex"][0]},'
                                                        f' got {v}'
                                                    )
                                            except re.error:
                                                pass
                            case t if 'choice:' in t or 'bool' in t:
                                if value not in token_details['values']:
                                    template_matches[template]['errors'].append(
                                        f'Invalid choice for {token_details["name"]},'
                                        f' got {value},'
                                        f' must be one of {", ".join(token_details["values"])}'
                                    )
                except Exception as e:
                    template_matches[template]['match'] = False
                    template_matches[template]['errors'].append(f'Error parsing URL: {str(e)}')
            else:
                template_matches[template]['match'] = False
                template_matches[template]['errors'].append('Invalid URL: does not match template')

        # if all templates failed to match, return False
        if all([not v['match'] for v in template_matches.values()]):
            return False, 'URL does not match any template'

        # if any template matched and has no errors, return True
        for template, details in template_matches.items():
            if details['match'] and not details['errors']:
                return True, None

        # if any template matched and has errors, return False
        matched_template_with_least_errors = min(
            [(t, d) for t, d in template_matches.items() if d['match']], key=lambda x: len(x[1]['errors'])
        )
        return False, matched_template_with_least_errors[1]['errors'][0]

    def send_test_message(self, urls: str | list[str]):
        if isinstance(urls, str):
            urls = [urls]
        if urls == ['test://test/test']:
            return True, None
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

    def generate_url_example(self, service_name, template=None):
        example = 'aaa://bbb/ccc'
        service = self.get_service_schema(service_name)
        if service is None:
            return example

        while not self.is_url_valid(example, service_name)[0]:
            service_details = service['details']
            if template and template in service_details['templates']:
                example = template
            else:
                example = self.faker.random_element(service_details['templates'])
            for token, details in service_details['tokens'].items():
                match details["type"]:
                    case 'int':
                        example = example.replace(
                            f'{{{token}}}',
                            str(self.faker.random_int(min=details.get('min', 0), max=details.get('max', 100))),
                        )
                    case 'float':
                        example = example.replace(
                            f'{{{token}}}',
                            str(
                                self.faker.pyfloat(
                                    min_value=details.get('min', 0.0), max_value=details.get('max', 100.0)
                                )
                            ),
                        )
                    case 'string':
                        if details.get('regex') is not None:
                            try:
                                example = example.replace(f'{{{token}}}', self.faker.regex(details['regex'][0]))
                            except re.error:
                                example = example.replace(f'{{{token}}}', self.faker.pystr(min_chars=5, max_chars=100))
                        else:
                            example = example.replace(f'{{{token}}}', self.faker.pystr(min_chars=5, max_chars=20))
                    case 'bool':
                        example = example.replace(f'{{{token}}}', self.faker.random_element(['true', 'false']))
                    case 'list:int':
                        delimiter = self.faker.random_element(details.get('delim', [',']))
                        example = example.replace(
                            f'{{{token}}}',
                            delimiter.join(
                                str(self.faker.random_int(min=details.get('min', 0), max=details.get('max', 100)))
                                for _ in range(self.faker.random_int(min=1, max=3))
                            ),
                        )
                    case 'list:float':
                        delimiter = self.faker.random_element(details.get('delim', [',']))
                        example = example.replace(
                            f'{{{token}}}',
                            delimiter.join(
                                str(
                                    self.faker.pyfloat(
                                        min_value=details.get('min', 0.0), max_value=details.get('max', 100.0)
                                    )
                                )
                                for _ in range(self.faker.random_int(min=1, max=3))
                            ),
                        )
                    case 'list:string':
                        delimiter = self.faker.random_element(details.get('delim', [',']))
                        if details.get('regex') is not None:
                            example = example.replace(
                                f'{{{token}}}',
                                delimiter.join(
                                    self.faker.regex(details['regex'][0])
                                    for _ in range(self.faker.random_int(min=1, max=3))
                                ),
                            )
                        elif details.get('group'):
                            selected_group = self.faker.random_element(details['group'])
                            group_details = service_details['tokens'][selected_group]
                            if group_details.get('alias_of'):
                                group_details = service_details['tokens'][group_details['alias_of']]
                            if group_details.get('regex') is not None:
                                example = example.replace(
                                    f'{{{token}}}',
                                    delimiter.join(
                                        self.faker.regex(group_details['regex'][0])
                                        for _ in range(self.faker.random_int(min=1, max=3))
                                    ),
                                )
                            else:
                                example = example.replace(
                                    f'{{{token}}}',
                                    delimiter.join(
                                        self.faker.pystr(min_chars=5, max_chars=20)
                                        for _ in range(self.faker.random_int(min=1, max=3))
                                    ),
                                )
                        else:
                            example = example.replace(
                                f'{{{token}}}',
                                delimiter.join(
                                    self.faker.pystr(min_chars=5, max_chars=20)
                                    for _ in range(self.faker.random_int(min=1, max=3))
                                ),
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
                html += f'<li>{template.replace("{schema}", schema)}</li>'
        html += '</ul>'
        html += '<h2>Tokens</h2>'
        html += '<table class="table">'
        html += '<tr><th>Token</th><th>Required</th><th>Type</th><th>Constraints</th></tr>'
        for token_name, details in sorted(
            service_details['tokens'].items(), key=lambda x: (not x[1]['required'], x[1]['name'])
        ):
            if token_name == 'schema':
                continue
            html += f'<tr><td>{details["name"]}</td>'
            html += f'<td>{"Yes" if details["required"] else "No"}</td>'
            match details["type"]:
                case 'int':
                    html += '<td>Integer</td>'
                case 'float':
                    html += '<td>Float</td>'
                case 'string':
                    html += '<td>String</td>'
                case 'list:int':
                    html += '<td>List of integers</td>'
                case 'list:float':
                    html += '<td>List of floats</td>'
                case 'list:string':
                    html += '<td>List of strings</td>'
                case t if 'choice:' in t or 'bool' in t:
                    html += '<td>Choice</td>'
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
        html += (
            "<p>For obtaining the required tokens, visit the "
            f"<a href='{service['service_url']}' target='_blank'>service's page</a>."
            "<br>"
            "For more parameters and examples, visit the "
            f"<a href='{service['setup_url']}' target='_blank'>documentation</a>.</p>"
        )
        return html
