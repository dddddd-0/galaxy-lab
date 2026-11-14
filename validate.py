"""Write a reproducible sampling report, with calibration caveat attached."""
import json
from pathlib import Path
from model import ensemble, VERSION

if __name__=='__main__':
    report=ensemble(2000,12)
    report['model']=VERSION
    report['validation_scope']='Implementation sampling diagnostics; not a goodness-of-fit test against astronomical observations.'
    target=Path(__file__).resolve().parent/'sampling-report.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
