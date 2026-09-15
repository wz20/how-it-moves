"""Course evidence and teacher handoff. Never infer approval or publish private materials."""
from __future__ import annotations
import json
from pathlib import Path
import topic_model as m


def blank_course():
    return {'audience':'','objectives':[],'prerequisites':[],'scope':'','assumptions':[],
        'sources':[],'claims':[],'equations':[],'misconceptions':[], 'assessment':[],
        'privacy':{'third_party_upload':False,'public_publish':False},
        'teacher_review':{'verdict':'pending','note':'Use a separate teacher-review.json tied to the artifact fingerprint.'}}


def validate_course(data, final=False):
    profile=data.get('profile','general')
    m.require(profile in ('general','academic'),'E_COURSE','profile must be general/academic')
    if profile!='academic':return
    c=data.get('course');m.require(isinstance(c,dict),'E_COURSE','academic projects require course goals and an evidence ledger')
    for k in ('audience','scope'):m.string(c.get(k),'course.'+k,800)
    for k in ('objectives','assumptions','assessment'):
        m.require(isinstance(c.get(k),list) and c[k],'E_COURSE','course.'+k+' must be explicit')
        for v in c[k]:m.string(v,'course.'+k,1000)
    for k in ('prerequisites','misconceptions'):
        m.require(isinstance(c.get(k),list),'E_COURSE','course.'+k+' must be a list')
        for v in c[k]:m.string(v,'course.'+k,1000)
    sources=c.get('sources');m.require(isinstance(sources,list) and 1<=len(sources)<=100,'E_COURSE','supply verified course/primary references')
    ids=set()
    for source in sources:
        m.require(isinstance(source,dict),'E_COURSE','source must be an object')
        for k in ('id','title','reference'):m.string(source.get(k),'source.'+k,1200)
        m.require(source['id'] not in ids,'E_COURSE','duplicate source ID');ids.add(source['id'])
        m.require(source.get('kind') in ('user-material','primary-document'),'E_COURSE','identify the actual source type')
    claims=c.get('claims');m.require(isinstance(claims,list) and claims,'E_COURSE','map factual claims to specific sources')
    claim_ids=set()
    for claim in claims:
        m.require(isinstance(claim,dict),'E_COURSE','claim must be an object')
        for k in ('id','statement','locator'):m.string(claim.get(k),'claim.'+k,1800)
        m.require(claim['id'] not in claim_ids,'E_COURSE','duplicate claim');claim_ids.add(claim['id'])
        refs=claim.get('source_ids');m.require(isinstance(refs,list) and refs and all(type(x) is str and x in ids for x in refs),'E_CLAIM_SOURCE','claim must cite an existing source and exact section/page')
        m.require(claim.get('status') in ('pending','verified'),'E_COURSE','claim status must be pending/verified')
        if final:
            m.require(claim['status']=='verified','E_CLAIM_REVIEW','verify '+claim['id']+' before a reviewed artifact export')
            m.string(claim.get('checked_by'),'claim.checked_by',200)
    equations=c.get('equations');m.require(isinstance(equations,list),'E_COURSE','equations list required, empty when there are none')
    for eq in equations:
        m.require(isinstance(eq,dict),'E_EQUATION','equation must include expression, domain, units and symbols')
        for k in ('expression','domain','unit_check'):m.string(eq.get(k),'equation.'+k,1200)
        symbols=eq.get('symbols');m.require(isinstance(symbols,dict) and symbols,'E_EQUATION','symbols and units required')
        for k,v in symbols.items():m.string(k,'symbol',40);m.string(v,'unit/meaning',300)
        m.require(isinstance(eq.get('source_ids'),list) and eq['source_ids'] and all(type(x) is str and x in ids for x in eq['source_ids']),'E_CLAIM_SOURCE','equation source missing')
        if final:m.string(eq.get('checked_by'),'equation.checked_by',200)
    privacy=c.get('privacy');m.require(isinstance(privacy,dict) and all(type(privacy.get(k)) is bool for k in ('third_party_upload','public_publish')),'E_PRIVACY','record explicit upload/publication consent; defaults are false')


def assert_publishable_assets(data):
    for a in data.get('assets',[]):
        gen=a.get('generation',{})
        joined=' '.join(str(gen.get(k,'')) for k in ('tool','model','run_reference','prompt')).lower()
        m.require(not any(x in joined for x in ('synthetic-unit','not a model','test-fixture','regression-only','test only')),
                  'E_TEST_ASSET','test fixtures cannot become a client handoff: '+str(a.get('id')))


def teacher_template(fingerprint, delivery_hash):
    return {'schema_version':1,'source_fingerprint':fingerprint,'delivery_sha256':delivery_hash,'verdict':'pending',
       'reviewer':'','role':'','request_reference':'','findings':{
          'factual_accuracy':'','equations_units_assumptions':'','learning_objectives':'','visual_explanation':'','accessibility_and_playback':''}}


def check_teacher(data, fingerprint, review_file, delivery_hash=None):
    validate_course(data,final=True)
    p=Path(review_file)
    m.require(p.is_file(),'E_TEACHER_REVIEW','instructor/subject reviewer sign-off is missing')
    review=json.loads(p.read_text(encoding='utf-8'))
    m.require(review.get('verdict')=='approved','E_TEACHER_REVIEW','subject review is pending/rejected')
    m.require(review.get('source_fingerprint')==fingerprint,'E_TEACHER_REVIEW','teacher approved a different source version')
    if delivery_hash is not None:m.require(review.get('delivery_sha256')==delivery_hash,'E_TEACHER_REVIEW','teacher approved a different delivery')
    for k in ('reviewer','role','request_reference'):m.string(review.get(k),'teacher.'+k,400)
    m.require(review['role'] in ('instructor','subject-reviewer'),'E_TEACHER_REVIEW','visual agent approval is not subject review')
    for k in ('factual_accuracy','equations_units_assumptions','learning_objectives','visual_explanation','accessibility_and_playback'):
        m.string(review.get('findings',{}).get(k),'teacher.findings.'+k,2000)
    return review


def verified_delivery(directory):
    """Use the exact exported manifest; don't collect arbitrary client working files."""
    root=Path(directory).resolve();manifest=root/'delivery.json'
    m.require(manifest.is_file(),'E_HANDOFF','delivery.json missing; export a reviewed artifact first')
    report=json.loads(manifest.read_text(encoding='utf-8'))
    m.require(isinstance(report.get('files'),dict) and report['files'],'E_HANDOFF','empty delivery')
    allowed={'animation.html','illustration.svg','video.mp4'}
    for name,entry in report['files'].items():
        m.require(name in allowed,'E_HANDOFF','unrecognized media in delivery manifest')
        p=m.local(root,name);m.require(m.sha(p)==entry.get('sha256') and p.stat().st_size==entry.get('bytes'),'E_HANDOFF','changed exported artifact: '+name)
    return root,report,m.sha(manifest)


def prepare_handoff(data,project,delivery,destination):
    import topic_output as out
    validate_course(data,final=True)
    root,report,digest=verified_delivery(delivery)
    fp=out.fingerprint(data,project)
    m.require(report.get('source_fingerprint')==fp,'E_HANDOFF','delivery belongs to a different source version')
    target=Path(destination).resolve()
    m.require(target.is_relative_to(Path(project).resolve()) and not target.exists(),'E_HANDOFF','use a new teacher review file in the project')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(teacher_template(fp,digest),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return target


def handoff(data,project,delivery,teacher_file,destination):
    import shutil,tempfile
    import topic_output as out
    m.require(data.get('profile')=='academic','E_HANDOFF','this handoff is the academic/subject-review path')
    assert_publishable_assets(data);validate_course(data,final=True)
    root,report,digest=verified_delivery(delivery);fp=out.fingerprint(data,project)
    m.require(report.get('source_fingerprint')==fp,'E_HANDOFF','re-export changed source before customer handoff')
    rp=Path(teacher_file).resolve()
    m.require(rp.is_relative_to(Path(project).resolve()),'E_TEACHER_REVIEW','teacher record must be in the project')
    teacher=check_teacher(data,fp,rp,digest)
    dest=Path(destination).resolve();m.require(not dest.exists(),'E_EXISTS','use a new handoff directory')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.academic-handoff-',dir=dest.parent) as tmp:
        tmp=Path(tmp)
        for name in report['files']:shutil.copy2(root/name,tmp/name)
        c=data['course'];notes=['# 教学演示交付说明',data['topic'],'','## 教学目标',*c['objectives'],'','## 适用范围',c['scope'],'','## 简化与假设',*c['assumptions'],'','## 检查问题',*c['assessment'],'','## 引用资料']
        notes += [f'{s["id"]} | {s["title"]} | {s["reference"]}' for s in c['sources']]
        notes += ['','本件为教师/学科审阅后的教学示意，不等于实测系统录像、物理仿真或学习效果已验证。','客户素材不会由此命令上传到 GitHub 或其他服务。']
        (tmp/'教学说明.md').write_text('\n'.join(notes)+'\n',encoding='utf-8')
        record={'status':'subject-reviewed-handoff','source_fingerprint':fp,'delivery_sha256':digest,
          'reviewer':teacher['reviewer'],'teaching_outcome':'not_tested','public_publish':False,
          'files':{p.name:m.sha(p) for p in tmp.iterdir()}}
        (tmp/'handoff.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        dest.mkdir()
        for p in tmp.iterdir():p.rename(dest/p.name)
    return record
