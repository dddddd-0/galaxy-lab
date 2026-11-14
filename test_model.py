import json
import math
import random
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from model import population, system, catalog, ensemble, imf, poisson
from server import Handler

class ModelTests(unittest.TestCase):
    def test_identity_independent_of_query_order_and_lod(self):
        before=system(75,42)
        for i in reversed(range(100)): population(i,42)
        self.assertEqual(before,system(75,42))
        self.assertEqual(catalog(42,100)['objects'],catalog(42,200)['objects'][:100])
        self.assertNotEqual(population(75,42),population(75,43))

    def test_imf_integral(self):
        r=random.Random(70)
        n=40000
        observed=sum(imf(r)<0.5 for _ in range(n))/n
        low=(0.5**(-.3)-.08**(-.3))/(-.3)
        high=.5*(100**(-1.3)-.5**(-1.3))/(-1.3)
        self.assertLess(abs(observed-low/(low+high)),.012)

    def test_poisson_moments(self):
        import statistics
        r=random.Random(19)
        values=[poisson(r,2.5) for _ in range(20000)]
        self.assertLess(abs(statistics.mean(values)-2.5),.06)
        self.assertLess(abs(statistics.variance(values)-2.5),.12)

    def test_population_and_orbit_invariants(self):
        c=catalog(42,3000)
        self.assertEqual(sum(c['counts'].values()),3000)
        self.assertEqual(len({o['id'] for o in c['objects']}),3000)
        for i in range(3000):
            s=system(i,42); host=s['host'];last=0
            self.assertGreater(host['mass_solar'],0)
            self.assertTrue(all(math.isfinite(v) for v in host['position_kpc']))
            if host['kind']!='star': self.assertEqual(s['planets'],[])
            for p in s['planets']:
                a=p['semi_major_axis_au']
                self.assertGreater(a,last); self.assertLessEqual(a,100)
                self.assertLess(p['eccentricity'],1)
                self.assertAlmostEqual(p['period_years']**2,a**3/host['mass_solar'],delta=max(.01,a**3/host['mass_solar']*.001))
                last=a

    def test_ensemble_bookkeeping(self):
        e=ensemble(300,4)
        self.assertAlmostEqual(sum(e['metrics'][kind]['mean'] for kind in ['star','white_dwarf','neutron_star','black_hole']),300)
        self.assertGreater(e['metrics']['planets']['sample_variance'],0)
        self.assertIn('not_observational',e['status'])

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.worker=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.worker.start()
        cls.base=f'http://127.0.0.1:{cls.http.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.worker.join()
    def test_contract(self):
        for path in ['/','/app.js','/style.css','/api/catalog?n=100&seed=42','/api/system?index=2&seed=42','/api/ensemble?n=100&runs=2']:
            with urllib.request.urlopen(self.base+path) as response:
                body=response.read();self.assertEqual(response.status,200)
                if path.startswith('/api/'): self.assertIsInstance(json.loads(body),dict)
    def test_limits(self):
        for path in ['/api/catalog?n=99999999','/api/catalog?seed=-1','/api/system?index=-1','/api/ensemble?runs=1','/api/catalog?n=nan','/api/unknown']:
            with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(self.base+path)
            self.assertIn(error.exception.code,[400,404])

if __name__=='__main__':unittest.main(verbosity=2)
