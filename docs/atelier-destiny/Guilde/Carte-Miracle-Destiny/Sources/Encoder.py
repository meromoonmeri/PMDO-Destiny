"""Transcode the captured frame sequence, with one synchronous jingle per discovery."""
from pathlib import Path
import json, subprocess, sys

root=Path(__file__).resolve().parents[1]; cache=Path(sys.argv[1]).resolve()
cap=json.loads((cache/'capture.json').read_text());fps=cap['fps'];frames=cap['frames'];duration=frames/fps
clouds=cap.get('edition')=='nuages'
m=len(cap['signals']);assert m==(9 if clouds else 5)
split=''.join(f'[s{i}]' for i in range(m));mix=''.join(f'[d{i}]' for i in range(m))
filters=[f'[1:a]asplit={m}{split}'];filters.extend(f'[s{i}]adelay={j["ms"]}:all=1[d{i}]' for i,j in enumerate(cap['signals']))
filters.append(f'{mix}amix=inputs={m}:normalize=0,apad,alimiter=limit=0.88:level=0:latency=1[a]')
mp4=root/('Ouverture-des-nuages-Destiny.mp4' if clouds else 'Apercu-Expedition-Destiny.mp4');tmp=cache/'video-encodee.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-i',str(cache/'%05d.jpg'),'-i',str(root/'Calques/Signal-Decouverte.mp3'),
 '-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
 '-c:v','libx264','-crf','22' if clouds else '21','-preset','fast','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',
 '-c:a','aac','-ar','48000','-b:a','144k','-t',str(duration),'-movflags','+faststart',str(tmp)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(tmp)]));v,a=probe['streams']
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and [v['width'],v['height']]==cap['dimensions']
assert int(v['nb_frames'])==frames and abs(float(probe['format']['duration'])-duration)<.02
assert a['codec_name']=='aac' and a['sample_rate']=='48000'
# The completed container and stream checks above precedes replacement of the previous demo.
mp4.write_bytes(tmp.read_bytes())
(root/('Verification-video-nuages.json' if clouds else 'Verification-video.json')).write_text(json.dumps({'statut':'PASS',**cap,'duree':duration,'video':'H.264','audio':'AAC, 48 kHz','lieux_fixes':True},ensure_ascii=False,indent=2)+'\n')
print(f'{mp4.name}: {duration:g} s à {fps} images/s · {m} découvertes · {mp4.stat().st_size:,} octets')
