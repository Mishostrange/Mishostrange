import sys
import unittest
from pathlib import Path
from datetime import date,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from public_calendar import parse_calendar

class CalendarTests(unittest.TestCase):
    def fixture(self):
        html='<h2 id="js-contribution-activity-description">1 contribution in the last year</h2>'
        for i in range(365):
            day=date(2025,10,13)+timedelta(days=i)
            level=1 if i==4 else 0
            tooltip='1 contribution on October 17th.' if i==4 else 'No contributions on a date.'
            html+=f'<td id="d{i}" class="ContributionCalendar-day" data-date="{day}" data-level="{level}"></td><tool-tip for="d{i}">{tooltip}</tool-tip>'
        return html

    def test_verified_counts_and_sunday_alignment(self):
        data=parse_calendar(self.fixture())
        self.assertEqual(data['totalContributions'],1)
        self.assertEqual(data['weeks'][0]['contributionDays'][0]['weekday'],1)

    def test_refuses_missing_tooltips_and_wrong_total(self):
        with self.assertRaises(ValueError):
            parse_calendar(self.fixture().replace('for="d4"','for="wrong"'))
        with self.assertRaises(ValueError):
            parse_calendar(self.fixture().replace('1 contribution in the last year','99 contributions in the last year'))

    def test_refuses_partial_or_changed_markup(self):
        with self.assertRaises(ValueError):
            parse_calendar('<html>GitHub is unavailable</html>')

if __name__=='__main__':
    unittest.main()
