import logging

import keys

from tropofy import main as tropofy_main, serve_app_cascade

logging.basicConfig()

apps_config = {
    'tropofy': {
        'api_url': 'https://api.tropofy.com',
        'auth_url': 'https://auth.tropofy.com',
    },
    'database': {
        'url': 'sqlite:///database.db',
    },
    'apps': [
        {
            'module': 'app',
            'classname': 'Application',
            'config': {
                'key.public': keys.public,
                'key.private': keys.private,
            }
        }
    ]
}


tropofy_app = tropofy_main(apps_config)

if __name__ == "__main__":
    serve_app_cascade(tropofy_app, '0.0.0.0', 8080)
