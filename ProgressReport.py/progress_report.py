from datetime import datetime, timedelta


class ProgressReport:
    def __init__(self, N: int, min_interval_seconds: int = 2):
        self.N = N
        self.min_interval = timedelta(seconds=min_interval_seconds)
        self.start = self._now()
        self.last_print = datetime.min
        self.last_line_len = 0

    def print_progress(self, i, text='', last: bool = False):
        now = self._now()

        skip = now - self.last_print < self.min_interval
        if skip and (not last) and i != self.N:
            return
        self.last_print = now
        dt = now - self.start

        pp = i * 100 // self.N if self.N != 0 else 100
        zero_of_zero = i == 0 and self.N == 0

        if zero_of_zero or i == 0 or i > self.N:
            result = f'\r{dt}, {i}/{self.N} = {pp}% {text}'
        else:
            remaining = self._predict_remaining(now, i)
            finish = now + remaining
            dt = timedelta(seconds=int(dt.total_seconds()))
            remaining = timedelta(seconds=int(remaining.total_seconds()))
            result = f'\r{dt} + {remaining} -> {finish:%b %d %H:%M:%S}, {i}/{self.N} = {pp}% {text}'

        dl = self.last_line_len - len(result)
        if dl > 0:
            result += ' ' * dl
        self.last_line_len = len(result)

        print(result, end='' if not last else '\n')

    def _predict_remaining(self, now: datetime, i: int) -> timedelta | None:
        # todo: handle i and N <=0
        if i == 0:
            return timedelta(0) if self.N == 0 else None
        dt = now - self.start
        finish = dt * (self.N - i) / i
        return finish

    def _now(self) -> datetime:
        return datetime.now()
