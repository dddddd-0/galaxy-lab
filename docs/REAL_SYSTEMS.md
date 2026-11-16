# 真实恒星系锚点（玩具数据）

界面里的金色菱形来自 `real_systems.py` 中的手工小样本。它不是 Gaia 或 NASA Exoplanet Archive 的实时镜像，也不声称是完整目录。

## 收录对象

| 系统 | 类型 | 距离（pc） | 本数据集行星数 | 备注 |
|---|---|---:|---:|---|
| 太阳系 | G2V | 0 | 8 | 我们所在的行星系统 |
| 南门二 / Alpha Centauri | G2V + K1V | 1.339 | 0 | 最近的恒星系统之一 |
| 比邻星 / Proxima Centauri | M5.5Ve | 1.301 | 3 | 最近的系外行星宿主之一 |
| 巴纳德星 | M4V | 1.828 | 0 | 高自行红矮星 |
| 天狼星 | A1V + DA2 | 2.637 | 0 | 夜空最亮恒星 |
| 织女星 | A0V | 7.68 | 0 | 尘埃盘 |
| 参宿四 | M1-2Ia-ab | 168 | 0 | 红超巨星 |
| 飞马座51 / 51 Pegasi | G2IV | 15.45 | 1 | 1995 年首颗主序星系外行星 |
| HD 209458 | G0V | 48.3 | 1 | 首批凌星系外行星之一 |
| TRAPPIST-1 | M8V | 12.47 | 7 | 七颗类地行星 |
| 开普勒-452 | G2V | 550 | 1 | 宜居带附近候选系统 |
| PSR B1257+12 | 脉冲星 | 710 | 3 | 1992 年首批确认系外行星 |

## 怎么算的

- J2000 赤经赤纬 + 距离 → 银道坐标 → 与 `model.py` 相同的银心坐标系。
- 太阳固定在 `[8.2, 0, 0.0208] kpc`，银心在原点。
- 不包含历元传播、视差误差、双星轨道、行星轨道倾角或动力学稳定性计算。
- 行星质量/半长轴/周期是展示用近似值；质量未测定时显示“未测定”。
- 来源页以 NASA Exoplanet Archive 和 SIMBAD 为主，界面中可直接打开。

## 为什么不直接下载全目录

真实目录接入需要目录版本、选择函数、交叉匹配和误差传播。先把玩具版本的“合成天体”和“真实锚点”明确分开，避免把几个手填值包装成已校准观测。下一步才是可复现的目录导入。

## 系外行星发现史时间线

时间线收录的是与当前恒星系锚点相关的代表性事件，年份指论文发表或公告时间，不代表发现工作的精确起始日。

| 年月 | 事件 | 系统 | 来源 |
|---|---|---|---|
| 1992-01 | 脉冲星行星首次确认 | PSR B1257+12 | [Wolszczan & Frail (1992)](https://ui.adsabs.harvard.edu/abs/1992Natur.355..145W/abstract) |
| 1995-10 | 51 Pegasi b 发表 | 51 Pegasi | [Mayor & Queloz (1995)](https://ui.adsabs.harvard.edu/abs/1995Natur.378..355M/abstract) |
| 1999-11 | 首次观测到系外行星凌星 | HD 209458 | [Charbonneau et al. (2000)](https://ui.adsabs.harvard.edu/abs/2000ApJ...529L..45C/abstract) |
| 2015-07 | Kepler-452 b 公布 | Kepler-452 | [Jenkins et al. (2015)](https://ui.adsabs.harvard.edu/abs/2015Sci...349..021J/abstract) |
| 2016-08 | Proxima Centauri b 公布 | 比邻星 | [Anglada-Escudé et al. (2016)](https://ui.adsabs.harvard.edu/abs/2016Natur.536..437A/abstract) |
| 2017-02 | TRAPPIST-1 七行星系统公布 | TRAPPIST-1 | [Gillon et al. (2017)](https://ui.adsabs.harvard.edu/abs/2017Natur.542..456G/abstract) |

界面事件可以定位到对应的手工近似坐标；论文链接在新标签页打开。
