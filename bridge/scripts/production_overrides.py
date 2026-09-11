import os, subprocess, shutil, sys
PROJECT=r'D:\first Blender'
SCRIPT=os.path.join(PROJECT,'bridge','scripts','build_production.py')
PKG=os.path.join(PROJECT,'bridge','python_packages')
if os.path.isdir(PKG) and PKG not in sys.path: sys.path.insert(0,PKG)
text=open(SCRIPT,'r',encoding='utf-8').read()
start=text.index('def speak(text,path,rate):')
end=text.index("for i,(sec,role,text) in enumerate(lines):", start)
new_block=r'''def speak(text,path,rate):
    mp3=path[:-4]+'.mp3'
    voices={'NARRATOR':'en-US-JennyNeural','MILO':'en-US-AnaNeural','PIP':'en-US-AnaNeural'}
    voice=voices.get(rate,'en-US-JennyNeural')
    try:
        import edge_tts, asyncio
        async def gen():
            c=edge_tts.Communicate(text,voice,rate='-4%' if voice.endswith('JennyNeural') else '+2%',pitch='+2Hz' if voice.endswith('AnaNeural') else '+0Hz',volume='+0%')
            await c.save(mp3)
        asyncio.run(gen())
        ff=shutil.which('ffmpeg')
        if not ff:
            import imageio_ffmpeg
            ff=imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([ff,'-y','-loglevel','error','-i',mp3,'-ar','48000','-ac','2',path],check=True)
    except Exception as e:
        print('NEURAL TTS ERROR:',repr(e))
        safe=text.replace("'","''"); pp=path.replace("'","''")
        cmd="$ErrorActionPreference='SilentlyContinue'; Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $v=$s.GetInstalledVoices() | Where-Object {$_.VoiceInfo.Gender -eq 'Female'} | Select-Object -First 1; if($v){$s.SelectVoice($v.VoiceInfo.Name)}; $s.Rate=0; $s.Volume=100; $s.SetOutputToWaveFile('%s'); $s.Speak('%s'); $s.Dispose()"%(pp,safe)
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',cmd],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

'''
text=text[:start]+new_block+text[end:]
text=text.replace("speak(text,p,0 if role=='NARRATOR' else (3 if role=='MILO' else 7))","speak(text,p,role)")
marker="# Magic seed rises into flower near finale."
anim=r'''
# Enhanced character performance: blinks, ear flaps, expressive waves and rabbit hops.
eye_objs=[o for o in bpy.data.objects if o.name.startswith('Eye')]
for f in range(90,END-20,170):
    for o in eye_objs:
        base=o.scale.z; o.scale.z=0.035; o.keyframe_insert(data_path='scale',frame=f)
        o.scale.z=base; o.keyframe_insert(data_path='scale',frame=f+6)
for o in [x for x in bpy.data.objects if x.name=='Ear' or x.name.startswith('Ear.')]:
    base=o.rotation_euler.y
    for f in range(1,END,144):
        o.rotation_euler.y=base+math.radians(7); o.keyframe_insert(data_path='rotation_euler',index=1,frame=f)
        o.rotation_euler.y=base-math.radians(5); o.keyframe_insert(data_path='rotation_euler',index=1,frame=f+18)
        o.rotation_euler.y=base; o.keyframe_insert(data_path='rotation_euler',index=1,frame=f+36)
for name,side in [('Arm',-1),('Arm.001',1)]:
    o=bpy.data.objects.get(name)
    if o:
        for sec in [35,100,150,245,345,465,525,585]:
            f=int(sec*FPS); base=o.rotation_euler.y
            o.rotation_euler.y=base+side*math.radians(22); o.keyframe_insert(data_path='rotation_euler',index=1,frame=f)
            o.rotation_euler.y=base-side*math.radians(16); o.keyframe_insert(data_path='rotation_euler',index=1,frame=f+12)
            o.rotation_euler.y=base; o.keyframe_insert(data_path='rotation_euler',index=1,frame=f+24)
for sec in [150,190,250,390,525,550]:
    f=int(sec*FPS); root.location.z=0; root.keyframe_insert(data_path='location',index=2,frame=f)
    root.location.z=.42; root.keyframe_insert(data_path='location',index=2,frame=f+12)
    root.location.z=0; root.keyframe_insert(data_path='location',index=2,frame=f+24)
for o in parts:
    if 'Pip Ear' in o.name:
        for f in range(1,END,192):
            o.rotation_euler.y=math.radians(8); o.keyframe_insert(data_path='rotation_euler',index=1,frame=f)
            o.rotation_euler.y=math.radians(-7); o.keyframe_insert(data_path='rotation_euler',index=1,frame=f+20)
            o.rotation_euler.y=0; o.keyframe_insert(data_path='rotation_euler',index=1,frame=f+40)
'''
text=text.replace(marker,anim+'\n'+marker)
open(SCRIPT,'w',encoding='utf-8').write(text)
print('PRODUCTION OVERRIDES APPLIED: neural female narration + enhanced animation')
