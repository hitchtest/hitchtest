from hitchtest.environment import checks

class HitchEnvironmentCheckUnavailableException(Exception):
    pass

def verify(rules):
    for rule in rules:
        key = list(rule.keys())[0]
        value = list(rule.values())[0]

        if hasattr(checks, key):
            getattr(checks, key)(value)
        else:
            raise HitchEnvironmentCheckUnavailableException("'{}' not available!".format(key))
