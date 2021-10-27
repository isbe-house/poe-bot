import logging


class Log:
    '''Generalized logging class for easy import.'''

    log = logging.getLogger('poe_lib')
    log.setLevel(logging.INFO)
    _ch = logging.StreamHandler()
    _formatter = logging.Formatter('{asctime} - {levelname} - {filename}:{lineno} - {funcName} - {message}', style='{')
    _ch.setFormatter(_formatter)
    log.addHandler(_ch)

    def __getattr__(self, name):
        '''Map in the logging class attributes.'''
        return getattr(self.log, name)
