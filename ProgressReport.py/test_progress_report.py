from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from progress_report import ProgressReport

class TestPredictRemaining(TestCase):
    def test_trivial(self):
        now = datetime.utcnow()
        target = ProgressReport(0)
        self.assertEqual(timedelta(0), target._predict_remaining(now, 0))

    def test_half(self):
        i = 5
        N = 15
        start = datetime(2022, 1, 1, 0, 0, 0)
        now = start + timedelta(hours=1)
        expected = timedelta(hours=2)

        target = ProgressReport(N)
        target.start = start
        actual = target._predict_remaining(now, i)

        self.assertEqual(expected, actual)

    def test_simple(self):
        i = 5
        N = 10
        start = datetime(2022, 1, 1, 0, 0, 0)
        now = start + timedelta(hours=1)
        expected = timedelta(hours=1)

        target = ProgressReport(N)
        target.start = start
        actual = target._predict_remaining(now, i)

        self.assertEqual(expected, actual)

    def test_undefined(self):
        i = 0
        N = 100
        start = datetime(2022, 1, 1, 0, 0, 0)
        now = start + timedelta(hours=1)

        target = ProgressReport(N)
        self.assertIsNone(target._predict_remaining(now, i))

    def test_done(self):
        N = 100
        start = datetime(2022, 1, 1, 0, 0, 0)
        now = start + timedelta(hours=1)

        target = ProgressReport(N)
        actual = target._predict_remaining(now, N)

        self.assertEqual(timedelta(0), actual)


class TestPrint(TestCase):
    @patch('builtins.print')
    def test_trivial(self, print_mock):
        target = ProgressReport(0)
        target.print_progress(0, 'text')
        expected_out = '\r0:00:00, 0/0 = 100% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_zero(self, now_mock, print_mock):
        now_mock.return_value = datetime(2022, 1, 1, 8, 0, 0)
        target = ProgressReport(10)
        now_mock.return_value = datetime(2022, 1, 1, 9, 0, 0)
        target.print_progress(0, 'text')
        expected_out = '\r1:00:00, 0/10 = 0% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_zero_of_zero(self, now_mock, print_mock):
        now_mock.return_value = datetime(2022, 1, 1, 8, 0, 0)
        target = ProgressReport(0)
        now_mock.return_value = datetime(2022, 1, 1, 9, 0, 0)
        target.print_progress(0, 'text')
        expected_out = '\r1:00:00, 0/0 = 100% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_simple(self, now_mock, print_mock):
        now_mock.return_value = datetime(2022, 1, 1, 8, 0, 0)
        target = ProgressReport(10)
        now_mock.return_value = datetime(2022, 1, 1, 9, 0, 0)
        target.print_progress(5, 'text')
        expected_out = '\r1:00:00 + 1:00:00 -> Jan 01 10:00:00, 5/10 = 50% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_nice(self, now_mock, print_mock):
        start = datetime(2022, 1, 1, 8, 0, 0, microsecond=100_000)
        now_mock.return_value = start
        target = ProgressReport(10)
        now_mock.return_value = start + timedelta(hours=1, milliseconds=100)
        target.print_progress(5, 'text')
        expected_out = '\r1:00:00 + 1:00:00 -> Jan 01 10:00:00, 5/10 = 50% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_done(self, now_mock, print_mock):
        now_mock.return_value = datetime(2022, 1, 1, 8, 0, 0)
        target = ProgressReport(10)
        now_mock.return_value = datetime(2022, 1, 1, 9, 0, 0)
        target.print_progress(10, 'text')
        expected_out = '\r1:00:00 + 0:00:00 -> Jan 01 09:00:00, 10/10 = 100% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_overdone(self, now_mock, print_mock):
        now_mock.return_value = datetime(2022, 1, 1, 8, 0, 0)
        target = ProgressReport(10)
        now_mock.return_value = datetime(2022, 1, 1, 9, 0, 0)
        target.print_progress(11, 'text')
        expected_out = '\r1:00:00, 11/10 = 110% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_should_skip_print(self, now_mock, print_mock):
        start = datetime(2022, 1, 1, 9)
        now_mock.return_value = start
        target = ProgressReport(10)
        target.print_progress(5, 'text')
        now_mock.return_value = start + timedelta(seconds=1)
        target.print_progress(9, 'text')
        expected_out = '\r0:00:00 + 0:00:00 -> Jan 01 09:00:00, 5/10 = 50% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_should_skip_overdone_print(self, now_mock, print_mock):
        start = datetime(2022, 1, 1, 9)
        now_mock.return_value = start
        target = ProgressReport(10)
        target.print_progress(5, 'text')
        now_mock.return_value = start + timedelta(seconds=1)
        target.print_progress(11, 'text')
        expected_out = '\r0:00:00 + 0:00:00 -> Jan 01 09:00:00, 5/10 = 50% text'
        print_mock.assert_called_once_with(expected_out, end='')

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_should_not_skip_print(self, now_mock, print_mock: MagicMock):
        start = datetime(2022, 1, 1, 9)
        now_mock.return_value = start
        target = ProgressReport(10, min_interval_seconds=2)
        now_mock.return_value = start + timedelta(seconds=3)
        target.print_progress(5, 'text')
        now_mock.return_value = start + timedelta(seconds=9)
        target.print_progress(9, 'text')
        expected_out = [
            call('\r0:00:03 + 0:00:03 -> Jan 01 09:00:06, 5/10 = 50% text', end=''),
            call('\r0:00:09 + 0:00:01 -> Jan 01 09:00:10, 9/10 = 90% text', end='')]
        print_mock.assert_has_calls(expected_out)

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_should_not_skip_done_print(self, now_mock, print_mock: MagicMock):
        start = datetime(2022, 1, 1, 9)
        now_mock.return_value = start
        target = ProgressReport(10, min_interval_seconds=2)
        now_mock.return_value = start + timedelta(seconds=3)
        target.print_progress(5, 'text')
        now_mock.return_value = start + timedelta(seconds=9)
        target.print_progress(10, 'text')
        expected_out = [
            call('\r0:00:03 + 0:00:03 -> Jan 01 09:00:06, 5/10 = 50% text', end=''),
            call('\r0:00:09 + 0:00:00 -> Jan 01 09:00:09, 10/10 = 100% text', end='')]
        print_mock.assert_has_calls(expected_out)

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_should_not_skip_100(self, now_mock, print_mock: MagicMock):
        start = datetime(2022, 1, 1, 9)
        now_mock.return_value = start
        target = ProgressReport(10, min_interval_seconds=2)
        now_mock.return_value = start + timedelta(seconds=3)
        target.print_progress(5, 'text')
        now_mock.return_value = start + timedelta(seconds=4)
        target.print_progress(10, 'text')
        expected_out = [
            call('\r0:00:03 + 0:00:03 -> Jan 01 09:00:06, 5/10 = 50% text', end=''),
            call('\r0:00:04 + 0:00:00 -> Jan 01 09:00:04, 10/10 = 100% text', end='')]
        print_mock.assert_has_calls(expected_out)

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_should_not_skip_last(self, now_mock, print_mock: MagicMock):
        start = datetime(2022, 1, 1, 9)
        now_mock.return_value = start
        target = ProgressReport(10, min_interval_seconds=2)
        now_mock.return_value = start + timedelta(seconds=5)
        target.print_progress(5, 'text')
        now_mock.return_value = start + timedelta(seconds=6)
        target.print_progress(6, 'text', last=True)
        expected_out = [
            call('\r0:00:05 + 0:00:05 -> Jan 01 09:00:10, 5/10 = 50% text', end=''),
            call('\r0:00:06 + 0:00:04 -> Jan 01 09:00:10, 6/10 = 60% text', end='\n')]
        print_mock.assert_has_calls(expected_out)

    @patch('builtins.print')
    @patch('progress_report.ProgressReport._now')
    def test_clean_previous(self, now_mock, print_mock: MagicMock):
        start = datetime(2022, 1, 1, 9)
        now_mock.return_value = start
        target = ProgressReport(10, min_interval_seconds=2)
        now_mock.return_value = start + timedelta(seconds=3)
        target.print_progress(5, 'long text')
        now_mock.return_value = start + timedelta(seconds=9)
        target.print_progress(9, 'text')
        expected_out = [
            call('\r0:00:03 + 0:00:03 -> Jan 01 09:00:06, 5/10 = 50% long text', end=''),
            call('\r0:00:09 + 0:00:01 -> Jan 01 09:00:10, 9/10 = 90% text     ', end='')]
        print_mock.assert_has_calls(expected_out)
