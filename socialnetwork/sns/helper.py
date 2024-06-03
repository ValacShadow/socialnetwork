from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import Throttled

class CustomUserRateThrottle(UserRateThrottle):
    def wait(self):
        # Get the remaining wait time from the parent class
        wait_time = super().wait()

        if wait_time:
            # Raise a Throttled exception with a custom message
            raise Throttled(detail={'message': 'Too many requests. Wait for {} seconds.'.format(int(wait_time)), 'wait': wait_time})
        
        return wait_time
