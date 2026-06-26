from pytest import Parser, FixtureRequest, fixture
import logging
from app import logging_config

'''
Настройка использования опции "--case" для запуска тестовых сценариев
'''

test_case_option = '--case'

def pytest_configure(config):
    logging.getLogger('urllib3').setLevel('INFO')

def pytest_addoption(parser: Parser):
    parser.addoption(test_case_option, 
                    action='store', 
                    default='full', 
                    choices=['offline', 'online', 'full'],
                    help='запуск теста для режима: offline, online или both (default)'
    )

@fixture(scope='session')
def test_case(request: FixtureRequest) -> str:
    return request.config.getoption(test_case_option)
