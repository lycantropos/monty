from hypothesis import (HealthCheck,
                        settings)

settings.register_profile('default',
                          max_examples=5,
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])
