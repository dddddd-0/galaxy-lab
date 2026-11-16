"""Deterministic, illustrative population synthesis. Not an observational calibration."""
import hashlib
import math
import random
import statistics
from collections import Counter

from real_systems import all_history_events, all_real_systems, get_real_system

VERSION = '0.2.0-illustrative'
SOURCES = [
    {'name': 'Kroupa 2001 IMF', 'url': 'https://arxiv.org/abs/astro-ph/0009005', 'use': 'Broken power-law slopes; illustrative implementation'},
    {'name': 'Gaia Archive', 'url': 'https://gea.esac.esa.int/archive/', 'use': 'Planned catalog ingestion; no Gaia objects bundled'},
    {'name': 'NASA Exoplanet Archive', 'url': 'https://exoplanetarchive.ipac.caltech.edu/', 'use': 'Landmark system planet parameters and planned occurrence calibration; not yet fitted'},
    {'name': 'SIMBAD', 'url': 'https://simbad.u-strasbg.fr/simbad/', 'use': 'Curated approximate positions, spectral types and distances for landmark systems'},
]

def rng_for(seed, object_id):
    raw = hashlib.sha256(f'{VERSION}|{seed}|{object_id}'.encode()).digest()
    return random.Random(int.from_bytes(raw[:16], 'big'))

def imf(rng):
    # Continuity at 0.5 Msun, explicitly normalized over 0.08..100 Msun.
    parts = [(0.08, 0.5, 1.3, 1.0), (0.5, 100.0, 2.3, 0.5)]
    weights = [c * (hi**(1-a)-lo**(1-a))/(1-a) for lo,hi,a,c in parts]
    u = rng.random() * sum(weights)
    lo, hi, a, _ = parts[0 if u < weights[0] else 1]
    return (lo**(1-a) + rng.random()*(hi**(1-a)-lo**(1-a)))**(1/(1-a))

def poisson(rng, mean):
    product, k, threshold = 1.0, 0, math.exp(-mean)
    while product > threshold:
        product *= rng.random()
        k += 1
    return k - 1

def population(index, seed):
    r = rng_for(seed, f'star/{index}')
    component = r.choices(['thin_disk','thick_disk','bulge','halo'], [0.78,0.12,0.09,0.01])[0]
    if component in ('thin_disk','thick_disk'):
        radius = min(25.0, r.gammavariate(2, 2.6 if component == 'thin_disk' else 2.0))
        # Non-axisymmetric illustration, not a measured spiral-arm fit.
        theta = r.uniform(0, 2*math.pi)
        if component == 'thin_disk' and r.random() < 0.4:
            theta = math.log(max(radius,0.1)/3)/math.tan(0.23) + r.randrange(4)*math.pi/2 + r.gauss(0,0.18)
        z = r.expovariate(1/(0.3 if component == 'thin_disk' else 0.9)) * r.choice([-1,1])
        x,y = radius*math.cos(theta),radius*math.sin(theta)
        age = r.uniform(0.01,10) if component == 'thin_disk' else r.uniform(8,12)
    else:
        radius = min(3.5,r.gammavariate(2,0.6)) if component == 'bulge' else math.exp(r.uniform(math.log(2), math.log(50)))
        phi,ct = r.uniform(0,2*math.pi),r.uniform(-1,1)
        x,y,z = radius*math.sqrt(1-ct*ct)*math.cos(phi),radius*math.sqrt(1-ct*ct)*math.sin(phi),radius*ct
        if component == 'bulge': y *= 0.55; z *= 0.5
        age = r.uniform(8,13)
    metallicity = r.gauss(-0.06*(math.hypot(x,y)-8.2),0.18) if component == 'thin_disk' else r.gauss({'thick_disk':-0.6,'bulge':-0.1,'halo':-1.5}[component],0.3)
    initial = imf(r)
    lifetime = 10*initial**-2.5
    kind, mass = 'star',initial
    if age > lifetime:
        if initial < 8: kind,mass = 'white_dwarf', min(1.35,0.109*initial+0.394)
        elif initial < 25: kind,mass = 'neutron_star',r.uniform(1.2,2.0)
        else: kind,mass = 'black_hole',max(3,initial*(0.15+0.15*max(0,min(1,-metallicity))))
        # Approximate extra displacement, not orbit integration.
        if kind in ('neutron_star','black_hole'):
            scale = 1.0 if kind == 'neutron_star' else 0.3
            x += r.gauss(0,scale); y += r.gauss(0,scale); z += r.gauss(0,scale)
    return {'id':f'syn-{index:08d}','index':index,'source':'synthetic','model':VERSION,
            'component':component,'position_kpc':[round(x,6),round(y,6),round(z,6)],
            'age_gyr':round(age,4),'metallicity_dex':round(metallicity,4),
            'initial_mass_solar':round(initial,5),'mass_solar':round(mass,5),'kind':kind}

def system(index, seed):
    host = population(index,seed)
    r = rng_for(seed,f'planets/{index}')
    planets=[]
    if host['kind'] == 'star':
        # Gamma-Poisson latent rate gives between-system overdispersion.
        mean = 2.5*max(0.4,min(1.6,host['mass_solar']**-0.2))*10**(0.15*host['metallicity_dex'])
        count = poisson(r,r.gammavariate(2,mean/2))
        axis = max(0.04,0.02*math.sqrt(host['mass_solar']))
        for k in range(count):
            axis *= r.uniform(1.6,2.8)
            if axis > 100: break
            m = math.exp(r.uniform(math.log(0.1),math.log(1000)))
            planets.append({'id':f'{host["id"]}-p{k+1}','semi_major_axis_au':round(axis,5),
                            'mass_earth':round(m,4),'eccentricity':round(r.betavariate(1,8),4),
                            'period_years':round(math.sqrt(axis**3/host['mass_solar']),5),'source':'synthetic'})
    return {'host':host,'planets':planets,'caveat':'Illustrative occurrence and spacing; no binary evolution, stellar tracks, dynamical stability proof or occurrence fit.'}

def catalog(seed=42,n=12000):
    stars=[population(i,seed) for i in range(n)]
    return {'seed':seed,'model':VERSION,'status':'illustrative_not_calibrated','units':'kpc',
            'count':n,'counts':dict(Counter(s['kind'] for s in stars)), 'objects':stars,
            'anchors':[{'id':'sgr-a','name':'银河系中心','position_kpc':[0,0,0],
                        'source':'coordinate_reference','kind':'central_reference',
                        'note':'Coordinate reference only, not a fitted SMBH model.'}],
            'real_systems':all_real_systems(),'history_events':all_history_events(),
            'sources':SOURCES,'limitations':['Synthetic population parameters illustrative','One progenitor per sample; no binaries','No calibrated selection function','No total-Galaxy count extrapolation','Real landmark systems are a small curated approximate set, not a live catalog import']}

def real_system(system_id):
    return get_real_system(system_id)

def ensemble(n=2000,runs=12):
    counts=[]; planet_counts=[]
    for seed in range(runs):
        rows=[system(i,seed) for i in range(n)]
        counts.append(Counter(row['host']['kind'] for row in rows))
        planet_counts.append(sum(len(row['planets']) for row in rows))
    metrics={}
    for kind in ['star','white_dwarf','neutron_star','black_hole']:
        data=[c[kind] for c in counts]
        metrics[kind]={'mean':statistics.mean(data),'sample_variance':statistics.variance(data),'min':min(data),'max':max(data)}
    metrics['planets']={'mean':statistics.mean(planet_counts),'sample_variance':statistics.variance(planet_counts),'min':min(planet_counts),'max':max(planet_counts)}
    return {'status':'sampling_diagnostics_only_not_observational_validation','runs':runs,'progenitors_per_run':n,'fixed_count':'progenitors','metrics':metrics}
