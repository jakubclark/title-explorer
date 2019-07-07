import asyncio
import logging
import logging.config as log_config

import aiotask_context as context


class RequestIDFilter(logging.Filter):

    def filter(self, record):
        cur_task = asyncio.Task.current_task()
        if not asyncio.Task.current_task():
            record.request_id = 'bootstrap'
            return True

        if not hasattr(cur_task, 'context'):
            record.request_id = None
            return True

        record.request_id = context.get('request_id')
        return True


log_settings = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filters': ['requestid']
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filters': ['requestid'],
            'filename': 'title_explorer.log'
        }
    },
    'filters': {
        'requestid': {
            '()': RequestIDFilter
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(request_id)s [%(levelname)s] %(name)s - %(message)s'
        },
    },
    'loggers': {
        __package__: {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'aiohttp.access': {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'aiohttp.web': {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'DEBUG'
        },
    }
}

log_config.dictConfig(log_settings)
log = logging.getLogger(__name__)
