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


@attr.s
class CoronaVirusDataDelta(object):
    id = attr.ib()
    country = attr.ib()
    state = attr.ib()
    state_name = attr.ib()
    confirmed_case_delta = attr.ib()
    recovered_case_delta = attr.ib()
    death_case_delta = attr.ib()


def get_data_delta(cvd_1, cvd_2):
    return CoronaVirusDataDelta(id='', country=cvd_1.country, state=cvd_1.state, state_name=cvd_1.state_name,
                                confirmed_case_delta=cvd_1.confirmed_case - cvd_2.confirmed_case,
                                recovered_case_delta=cvd_1.recovered_case - cvd_2.recovered_case,
                                death_case_delta=cvd_1.death_case - cvd_2.death_case)
