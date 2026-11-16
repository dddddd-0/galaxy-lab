"""Curated, approximate landmark systems for the toy Galaxy Lab.

This is deliberately a small hand-curated set with links back to authoritative
catalogues.  It is not a live Gaia/NASA Exoplanet Archive ingestion layer, and
positions/parameters are rounded for interactive use.
"""
import copy
import math

SUN_POSITION_KPC = (8.2, 0.0, 0.0208)
_SUN_RA_DEG = 0.0
_SUN_DEC_DEG = 0.0

# J2000 equatorial -> Galactic rotation matrix (standard IAU/SIMBAD values).
_GAL = (
    (-0.0548755604, -0.8734370902, -0.4838350155),
    ( 0.4941094279, -0.4448296300,  0.7469822445),
    (-0.8676661490, -0.1980763734,  0.4559837762),
)


def _radec_to_galactocentric(ra_deg, dec_deg, distance_pc):
    """Approximate J2000 position in the same galactocentric frame as model.py.

    The Sun is at +8.2 kpc on the x axis and the Galactic Centre is at the
    origin, following the convention already used by the prototype.  This is a
    toy coordinate transform: no epoch propagation, proper motion or parallax
    uncertainty is applied.
    """
    ra, dec = math.radians(ra_deg), math.radians(dec_deg)
    eq = (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))
    gx = sum(_GAL[0][i] * eq[i] for i in range(3))
    gy = sum(_GAL[1][i] * eq[i] for i in range(3))
    gz = sum(_GAL[2][i] * eq[i] for i in range(3))
    d = distance_pc / 1000.0
    # _GAL x points from the Sun towards the Galactic Centre, i.e. -x in the
    # prototype's frame where the Sun has positive x.
    return (SUN_POSITION_KPC[0] - d * gx,
            SUN_POSITION_KPC[1] + d * gy,
            SUN_POSITION_KPC[2] + d * gz)


def _planet(name, mass_earth, semi_major_axis_au, period_days, eccentricity=0.0,
            radius_earth=None, source='NASA Exoplanet Archive / SIMBAD'):
    return {
        'name': name,
        'mass_earth': mass_earth,
        'radius_earth': radius_earth,
        'semi_major_axis_au': semi_major_axis_au,
        'period_days': round(period_days, 5),
        'period_years': round(period_days / 365.25, 7),
        'eccentricity': eccentricity,
        'source': source,
    }


def _system(name, name_en, ra_deg, dec_deg, distance_pc, spectral_type,
            mass_solar, planets, summary, source_url, kind='real_star_system',
            aliases=None):
    x, y, z = _radec_to_galactocentric(ra_deg, dec_deg, distance_pc)
    return {
        'id': 'real-' + name_en.lower().replace(' ', '-').replace('*', 'star').replace('+', 'plus'),
        'name': name,
        'name_en': name_en,
        'aliases': aliases or [],
        'kind': kind,
        'source': 'curated_real_approximation',
        'data_quality': 'approximate_curated_toy',
        'position_kpc': [round(x, 6), round(y, 6), round(z, 6)],
        'ra_deg': ra_deg,
        'dec_deg': dec_deg,
        'distance_pc': distance_pc,
        'spectral_type': spectral_type,
        'mass_solar': mass_solar,
        'planets': planets,
        'planet_count': len(planets),
        'summary': summary,
        'source_url': source_url,
        'note': ('手工整理的近似玩具数据；位置由 J2000 赤经赤纬和距离换算，未做历元传播、'
                 '视差误差、双星轨道或实时目录更新。行星参数以来源页为准。'),
    }


REAL_SYSTEMS = [
    _system(
        '太阳系', 'Solar System', 0.0, 0.0, 0.0, 'G2V', 1.0,
        [
            _planet('水星', 0.055, 0.387, 87.969, 0.206, 0.383),
            _planet('金星', 0.815, 0.723, 224.701, 0.007, 0.949),
            _planet('地球', 1.0, 1.0, 365.256, 0.017, 1.0),
            _planet('火星', 0.107, 1.524, 686.980, 0.093, 0.532),
            _planet('木星', 317.8, 5.204, 4332.59, 0.049, 11.21),
            _planet('土星', 95.2, 9.583, 10759.22, 0.057, 9.45),
            _planet('天王星', 14.5, 19.201, 30688.5, 0.046, 4.01),
            _planet('海王星', 17.1, 30.047, 60182.0, 0.011, 3.88),
        ],
        '我们所在的行星系统；这里是唯一按 1:1 日常尺度可直接理解的锚点。',
        'https://solarsystem.nasa.gov/',
    ),
    _system(
        '南门二', 'Alpha Centauri', 219.902058, -60.833992, 1.339, 'G2V + K1V', 1.079,
        [],
        '最近的恒星系统之一，由 A、B 两颗类太阳恒星组成；本数据集不收录未确认行星。',
        'https://simbad.u-strasbg.fr/simbad/sim-id?Ident=alf+Cen',
        aliases=['半人马座α', 'Rigil Kentaurus'],
    ),
    _system(
        '比邻星', 'Proxima Centauri', 217.42895, -62.67948, 1.301, 'M5.5Ve', 0.122,
        [
            _planet('Proxima Centauri d', 0.26, 0.02885, 5.122, 0.0),
            _planet('Proxima Centauri b', 1.07, 0.04857, 11.18418, 0.02),
            _planet('Proxima Centauri c', 7.0, 1.489, 1928.0, 0.04),
        ],
        '离太阳最近的恒星，也是离太阳最近的已知系外行星宿主之一。',
        'https://exoplanetarchive.ipac.caltech.edu/overview/Proxima%20Cen',
        aliases=['半人马座比邻星'],
    ),
    _system(
        '巴纳德星', 'Barnard\'s Star', 269.45208, 4.69339, 1.828, 'M4V', 0.144,
        [],
        '离太阳很近的高自行红矮星；本数据集不把候选信号当作已确认行星。',
        'https://simbad.u-strasbg.fr/simbad/sim-id?Ident=GJ+699',
        aliases=['GJ 699'],
    ),
    _system(
        '天狼星', 'Sirius', 101.28716, -16.71612, 2.637, 'A1V + DA2', 2.063,
        [],
        '夜空最亮恒星，A 星旁有一颗白矮星伴星；本数据集不收录未确认行星。',
        'https://simbad.u-strasbg.fr/simbad/sim-id?Ident=alf+CMa',
        aliases=['天狼', 'Sirius A'],
    ),
    _system(
        '织女星', 'Vega', 279.23473, 38.78369, 7.68, 'A0V', 2.135,
        [],
        '明亮的 A 型主序星，拥有尘埃盘；本数据集不收录未确认行星。',
        'https://simbad.u-strasbg.fr/simbad/sim-id?Ident=alf+Lyr',
        aliases=['织女一'],
    ),
    _system(
        '参宿四', 'Betelgeuse', 88.79294, 7.40706, 168.0, 'M1-2Ia-ab', 16.5,
        [],
        '红超巨星，已进入恒星演化晚期；它是玩具坐标中的真实恒星锚点，不是行星系统。',
        'https://simbad.u-strasbg.fr/simbad/sim-id?Ident=alf+Ori',
        aliases=['猎户座α'],
    ),
    _system(
        '飞马座51', '51 Pegasi', 344.36658, 20.76861, 15.45, 'G2IV', 1.11,
        [_planet('51 Pegasi b', 150.0, 0.0527, 4.2308, 0.013)],
        '1995 年发现第一颗围绕主序星运行的系外行星，是系外行星史上的里程碑。',
        'https://exoplanetarchive.ipac.caltech.edu/overview/51%20Peg',
        aliases=['Helvetios'],
    ),
    _system(
        'HD 209458', 'HD 209458', 330.79489, 18.88432, 48.3, 'G0V', 1.13,
        [_planet('HD 209458 b', 232.0, 0.04747, 3.52475, 0.0, 1.38)],
        '首批凌星系外行星之一，帮助建立了系外行星大气研究的方向。',
        'https://exoplanetarchive.ipac.caltech.edu/overview/HD%20209458',
        aliases=['Osiris'],
    ),
    _system(
        'TRAPPIST-1', 'TRAPPIST-1', 346.62237, -5.04140, 12.47, 'M8V', 0.089,
        [
            _planet('TRAPPIST-1 b', 0.33, 0.01154, 1.5109, 0.0),
            _planet('TRAPPIST-1 c', 1.37, 0.01580, 2.4218, 0.0),
            _planet('TRAPPIST-1 d', 0.41, 0.02227, 4.0496, 0.0),
            _planet('TRAPPIST-1 e', 0.69, 0.02925, 6.0996, 0.0),
            _planet('TRAPPIST-1 f', 0.68, 0.03849, 9.2066, 0.0),
            _planet('TRAPPIST-1 g', 0.94, 0.04683, 12.3529, 0.0),
            _planet('TRAPPIST-1 h', 0.33, 0.06189, 18.7729, 0.0),
        ],
        '一颗极小质量红矮星周围的七个已知类地行星，是玩具里最密集的“真实系”。',
        'https://exoplanetarchive.ipac.caltech.edu/overview/TRAPPIST-1',
    ),
    _system(
        '开普勒-452', 'Kepler-452', 296.00312, 44.27739, 550.0, 'G2V', 1.04,
        [_planet('Kepler-452 b', None, 1.046, 384.843, 0.0, 1.63)],
        '一颗位于宜居带附近的凌星系外行星候选系统；质量尚未精确测定。',
        'https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-452',
    ),
    _system(
        'PSR B1257+12', 'PSR B1257+12', 195.01250, 12.68250, 710.0, '脉冲星', 1.4,
        [
            _planet('PSR B1257+12 A', 0.020, 0.19, 25.262, 0.0),
            _planet('PSR B1257+12 B', 4.3, 0.36, 66.5419, 0.0),
            _planet('PSR B1257+12 C', 3.9, 0.46, 98.2114, 0.0),
        ],
        '1992 年确认第一组系外行星的脉冲星系统，是系外行星史的开端。',
        'https://exoplanetarchive.ipac.caltech.edu/overview/PSR%20B1257%2B12',
        aliases=['Lich'],
    ),
]


HISTORY_EVENTS = [
    {
        'date': '1992-01', 'year': 1992,
        'title': '脉冲星行星首次确认', 'system_id': 'real-psr-b1257plus12',
        'summary': 'PSR B1257+12 周围的行星信号得到确认，打开系外行星观测的新方向。',
        'source_url': 'https://ui.adsabs.harvard.edu/abs/1992Natur.355..145W/abstract',
    },
    {
        'date': '1995-10', 'year': 1995,
        'title': '51 Pegasi b 发表', 'system_id': 'real-51-pegasi',
        'summary': '发现围绕类太阳恒星运行的热木星，系外行星搜寻由此进入新阶段。',
        'source_url': 'https://ui.adsabs.harvard.edu/abs/1995Natur.378..355M/abstract',
    },
    {
        'date': '1999-11', 'year': 1999,
        'title': '首次观测到系外行星凌星', 'system_id': 'real-hd-209458',
        'summary': 'HD 209458 b 的凌星被观测到，使行星半径和大气研究成为可能。',
        'source_url': 'https://ui.adsabs.harvard.edu/abs/2000ApJ...529L..45C/abstract',
    },
    {
        'date': '2015-07', 'year': 2015,
        'title': 'Kepler-452 b 公布', 'system_id': 'real-kepler-452',
        'summary': '公布一颗围绕类太阳恒星、位于宜居带附近的凌星行星候选对象。',
        'source_url': 'https://ui.adsabs.harvard.edu/abs/2015Sci...349..021J/abstract',
    },
    {
        'date': '2016-08', 'year': 2016,
        'title': '发现 Proxima Centauri b', 'system_id': 'real-proxima-centauri',
        'summary': '在太阳最近邻星比邻星周围发现一颗低质量行星。',
        'source_url': 'https://ui.adsabs.harvard.edu/abs/2016Natur.536..437A/abstract',
    },
    {
        'date': '2017-02', 'year': 2017,
        'title': 'TRAPPIST-1 七行星系统', 'system_id': 'real-trappist-1',
        'summary': '公布围绕超冷矮星运行的七颗近地大小行星。',
        'source_url': 'https://ui.adsabs.harvard.edu/abs/2017Natur.542..456G/abstract',
    },
]


def all_real_systems():
    """Return a defensive copy so API callers cannot mutate the curated table."""
    return copy.deepcopy(REAL_SYSTEMS)


def all_history_events():
    return copy.deepcopy(HISTORY_EVENTS)


def get_real_system(system_id):
    for item in REAL_SYSTEMS:
        if item['id'] == system_id:
            return copy.deepcopy(item)
    return None
