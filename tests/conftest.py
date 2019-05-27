import os

from hypothesis import (HealthCheck,
                        settings)

print('environment keys', list(os.environ.keys()))
settings.register_profile('default',
                          max_examples=5,
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])
