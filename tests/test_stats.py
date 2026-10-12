import sys
import tempfile
import json
import unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import generate_stats as stats

class StatsTests(unittest.TestCase):
    def weeks(self,days):
        return [{'contributionDays':[{'date':day,'contributionCount':count} for day,count in days]}]

    def test_streak_includes_yesterday_before_today_activity(self):
        w=self.weeks([('2026-10-09',1),('2026-10-10',2),('2026-10-11',1),('2026-10-12',0)])
        self.assertEqual(stats.streaks(w,date(2026,10,12)),(3,3))

    def test_streak_resets_for_gap_and_ignores_future(self):
        w=self.weeks([('2026-10-07',1),('2026-10-08',1),('2026-10-10',0),('2026-10-12',2),('2026-10-13',1)])
        self.assertEqual(stats.streaks(w,date(2026,10,12)),(1,2))
        self.assertEqual(stats.streaks([],date(2026,10,12)),(0,0))

    def test_api_pagination_stars_forks_and_language_bytes(self):
        repo={'private':False,'fork':False,'stargazers_count':2,'full_name':'sample/code'}
        fork={**repo,'fork':True,'stargazers_count':5,'full_name':'sample/fork'}
        responses=[{'login':'sample','public_repos':101},[repo]*100,[fork],*[{'Python':10}]*100,[]]
        with patch.object(stats,'request',side_effect=responses) as api,patch.object(stats,'fetch_calendar',side_effect=ValueError('unavailable')):
            data=stats.fetch('sample','')
        self.assertEqual(data['stars'],205)
        self.assertEqual(data['languages'],{'Python':1000})
        self.assertIn('page=2',api.call_args_list[2].args[0])
        self.assertIsNone(data['calendar'])

    def test_graphql_failure_keeps_real_rest_stats(self):
        responses=[{'login':'sample','public_repos':0},[],[],{'errors':[{'message':'denied'}]}]
        with patch.object(stats,'request',side_effect=responses),patch.object(stats,'fetch_calendar',side_effect=ValueError('unavailable')):
            data=stats.fetch('sample','token')
        self.assertEqual(data['public_repos'],0)
        self.assertIsNone(data['calendar'])
        self.assertIn('unavailable',data['calendar_status'])

    def test_core_failure_retains_username_matched_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot=Path(folder)/'data.json'
            snapshot.write_text(json.dumps({'username':'sample','fetched_at':'2026-10-01 00:00 UTC'}))
            with patch.object(stats,'SNAPSHOT',snapshot),patch.object(stats,'config',return_value={'username':'sample'}),patch.dict(stats.os.environ,{},clear=True),patch.object(stats,'fetch',side_effect=RuntimeError('offline')),patch.object(stats,'render'):
                data,state=stats.generate()
            self.assertEqual(data['fetched_at'],'2026-10-01 00:00 UTC')
            self.assertTrue(state.startswith('STALE'))

    def test_snapshot_for_other_username_is_not_used(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot=Path(folder)/'data.json'
            snapshot.write_text(json.dumps({'username':'someoneelse'}))
            with patch.object(stats,'SNAPSHOT',snapshot),patch.object(stats,'config',return_value={'username':'sample'}),patch.dict(stats.os.environ,{},clear=True),patch.object(stats,'render'):
                data,state=stats.generate(offline=True)
            self.assertIsNone(data)

    def test_svg_escapes_api_text(self):
        from common import text
        self.assertIn('&lt;script&gt;',text(0,0,'<script>'))

if __name__=='__main__':
    unittest.main()
