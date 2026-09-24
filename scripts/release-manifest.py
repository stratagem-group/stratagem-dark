#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Freeze package bytes, detached signatures and metadata into a signed release manifest."""
import base64,hashlib,json,os,subprocess,sys,tarfile,urllib.request
from pathlib import Path
bundle,db=map(Path,sys.argv[1:3]); commit=sys.argv[3]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
metadata={}
for archive in sorted((db/'sync').glob('*.db')):
 with tarfile.open(archive) as t:
  for member in t.getmembers():
   if member.name.endswith('/desc'):
    text=t.extractfile(member).read().decode(); fields={}
    for part in text.strip().split('\n\n'):
     lines=part.splitlines();fields[lines[0].strip('%')]=lines[1:]
    if 'FILENAME' in fields:metadata[fields['FILENAME'][0]]=(archive.stem,fields)
packages=[]
for p in sorted((bundle/'repository').glob('*.pkg.tar.zst')):
 info=subprocess.check_output(['bsdtar','-xOf',str(p),'.PKGINFO'],text=True)
 fields={}
 for line in info.splitlines():
  k,sep,v=line.partition(' = ')
  if sep:fields.setdefault(k,[]).append(v)
 name=fields['pkgname'][0]; repository='stratagem-dark'
 if p.name in metadata:
  repository,m=metadata[p.name]
  if not p.with_name(p.name+'.sig').exists():
   if 'PGPSIG' not in m:raise SystemExit('Missing package signature: '+p.name)
   p.with_name(p.name+'.sig').write_bytes(base64.b64decode(m['PGPSIG'][0]))
  if m.get('SHA256SUM',[digest(p)])[0]!=digest(p):raise SystemExit('Repository checksum mismatch: '+p.name)
 subprocess.run(['pacman-key','--verify',str(p)+'.sig',str(p)],check=True)
 packages.append({'name':name,'version':fields['pkgver'][0],'architecture':fields['arch'][0],
                  'repository':repository,'file':'repository/'+p.name,'sha256':digest(p),
                  'signature':'repository/'+p.name+'.sig','licenses':fields.get('license',[]),
                  'source_url':fields.get('url',[''])[0],'depends':fields.get('depend',[])})
spdx={'spdxVersion':'SPDX-2.3','dataLicense':'CC0-1.0','SPDXID':'SPDXRef-DOCUMENT','name':'STRATAGEM DARK testing package inventory',
'documentNamespace':'https://github.com/stratagem-group/stratagem-dark/releases/'+commit,
'creationInfo':{'creators':['Tool: STRATAGEM DARK release-manifest'],'created':__import__('datetime').datetime.fromtimestamp(int(os.environ['SOURCE_DATE_EPOCH']),__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')},
'packages':[{'SPDXID':'SPDXRef-Package-'+str(i),'name':p['name'],'versionInfo':p['version'],'downloadLocation':p['source_url'] or 'NOASSERTION','filesAnalyzed':False,'licenseConcluded':'NOASSERTION','licenseDeclared':'NOASSERTION','checksums':[{'algorithm':'SHA256','checksumValue':p['sha256']}],'comment':'Package metadata declares: '+', '.join(p['licenses'])} for i,p in enumerate(packages)]}
(bundle/'sbom.spdx.json').write_text(json.dumps(spdx,indent=2)+'\n')
files={p.relative_to(bundle).as_posix():digest(p) for p in sorted(bundle.rglob('*')) if p.is_file()}
manifest={'schema_version':1,'product':'STRATAGEM DARK','version':'0.2.0-alpha2','source_commit':commit,'architecture':'x86_64','arch_snapshot':(bundle/'snapshot.txt').read_text().strip(),'builder_image':(bundle/'builder-image.txt').read_text().strip(),'repository_databases':{p.name:digest(p) for p in sorted((db/'sync').glob('*.db'))},'packages':packages,'files':files,'release_class':'testing'}
(bundle/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print('Locked and signature-verified',len(packages),'packages')
