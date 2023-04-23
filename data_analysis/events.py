# frequency counts every midnight. Thus minfreq 1 means that between 2 midnights there must be at least 1 event.
class FakeDiscreteLvl1Event:
    def __init__(self, profile, units_in_minutes: int, maxfreq, minfreq, restricted_hours, occured) -> None:
        self.profile = profile
        self.units_in_minutes = units_in_minutes
        self.maxfreq = maxfreq
        self.minfreq = minfreq
        self.restricted_hours = restricted_hours
        self.occured = occured
