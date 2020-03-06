import attr

@attr.s
class CoronaVirusData(object):
    id = attr.ib()
    country = attr.ib()
    state = attr.ib()
    state_name = attr.ib()
    confirmed_case = attr.ib()
    recovered_case = attr.ib()
    death_case = attr.ib()
