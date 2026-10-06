"""Parser and validation tests using temporary fixtures only; no new scientific measurements."""
import csv, hashlib, json, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
BASE = Path(__file__).resolve().parent
nb = json.loads((BASE / 'PQC_Automotive_Analysis_revised.ipynb').read_text())
namespace = dict(Path=Path, csv=csv, hashlib=hashlib, json=json, np=np, pd=pd)
exec(''.join(nb['cells'][4]['source']).split('package_manifest =')[0], namespace)
validate = namespace['validate_labels']; parse = namespace['parse_raw_manifest']; sha = namespace['sha256']
tidy = pd.read_csv(BASE/'pqc_tidy_timings.csv')
checks = []
def must_fail(label, fn):
    try: fn()
    except (ValueError, KeyError): checks.append(label); return
    raise AssertionError('Expected rejection: '+label)
for label, field, value in [('bad scenario','scenario','unknown'),('bad family','algorithm','Other'),('bad variant','variant','Other'),('bad operation','operation','Other'),('NaN','time_us',np.nan),('infinite','time_us',np.inf),('zero','time_us',0),('negative','time_us',-1)]:
    frame=tidy.copy();frame.loc[0,field]=value
    must_fail(label,lambda frame=frame:validate(frame))
must_fail('missing column',lambda:validate(tidy.drop(columns=['variant'])))
with tempfile.TemporaryDirectory() as td:
    root=Path(td); entries=[]
    for (sc,alg,op),group in tidy.groupby(['scenario','algorithm','operation']):
        path=root/f'{sc}_{alg}_{op}.csv'
        wide=pd.DataFrame({v:pd.Series(g.time_us.to_numpy()) for v,g in group.groupby('variant')})
        wide.to_csv(path,sep=';',index=False,encoding='utf-8-sig')
        entries.append(dict(path=path.name,sha256=sha(path),scenario=sc,algorithm=alg,operation=op,columns={c:c for c in wide.columns}))
    mp=root/'raw_manifest.json';mp.write_text(json.dumps({'schema_version':1,'files':entries}))
    parsed,_=parse(mp); keys=namespace['REQUIRED']
    pd.testing.assert_frame_equal(parsed[keys].sort_values(keys).reset_index(drop=True),tidy[keys].sort_values(keys).reset_index(drop=True),check_dtype=False,check_exact=True)
    checks.append('18-file fixture roundtrip preserves exact record multiset')
    one=entries[0];path=root/one['path'];good=path.read_bytes()
    with path.open('a') as f:f.write('Average;123;456\n')
    one['sha256']=sha(path);mp.write_text(json.dumps({'schema_version':1,'files':[one]}))
    must_fail('summary row',lambda:parse(mp))
    path.write_bytes(good+b'1;2\n');one['sha256']=sha(path);mp.write_text(json.dumps({'schema_version':1,'files':[one]}))
    must_fail('ragged row',lambda:parse(mp))
    path.write_bytes(good);one['sha256']='0'*64;mp.write_text(json.dumps({'schema_version':1,'files':[one]}))
    must_fail('checksum mismatch',lambda:parse(mp))
    one['path']='../escape.csv';mp.write_text(json.dumps({'schema_version':1,'files':[one]}))
    must_fail('path escape',lambda:parse(mp))
report={'status':'PASS','checks':checks,'scope':'Synthetic parser fixtures and invalid-input rejection; original raw dataset NOT tested.'}
(BASE/'analysis_outputs'/'parser_test_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
