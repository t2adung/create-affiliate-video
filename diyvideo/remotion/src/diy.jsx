import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, Audio, interpolate, spring, staticFile, useCurrentFrame,
  useVideoConfig, Easing} from 'remotion';
import '@fontsource/be-vietnam-pro/600.css';
import '@fontsource/be-vietnam-pro/700.css';
import '@fontsource/be-vietnam-pro/800.css';
import '@fontsource/be-vietnam-pro/900.css';

export const FPS = 30, W = 1080, H = 1920;
export const HOOK = 2 * FPS, END = 3 * FPS, LABEL_FRAMES = 3 * FPS, XFADE = 8;
export const stepFrames = (n) => Math.round(Math.min(3.0, 25 / n) * FPS);
export const totalFrames = (n) => HOOK + n * stepFrames(n) + END;
const SAFE = 60, BOTTOM = 320;
const FONT = "'Be Vietnam Pro', 'Noto Color Emoji', sans-serif";

function Sfx({at, name, volume = 0.5}) {
  return <Sequence from={at} layout="none"><Audio src={staticFile(`audio/${name}.wav`)} volume={volume} /></Sequence>;
}

function KenBurns({src, dur, variant = 0, blur = 0}) {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, dur], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
  const moves = [[1.0, 1.08, 0, -20], [1.08, 1.02, 15, 8], [1.03, 1.1, -18, 0], [1.07, 1.0, 0, 18]];
  const [a, b, dx, dy] = moves[variant % moves.length];
  return <AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
    <Img src={staticFile(src)} style={{width: W, height: H, objectFit: 'cover',
      transform: `scale(${a + (b - a) * p}) translate(${dx * p}px, ${dy * p}px)`,
      filter: blur ? `blur(${blur}px) brightness(.55)` : 'none'}} />
  </AbsoluteFill>;
}

function KeyClip({clip, still, dur}) {
  // interpolated hand motion (FFmpeg minterpolate), then the final step frame held for readability
  const f = useCurrentFrame();
  const playFrames = dur - Math.round(0.6 * FPS);
  return <AbsoluteFill style={{background: '#000'}}>
    {f < playFrames
      ? <OffthreadVideo src={staticFile(clip)} muted style={{width: W, height: H, objectFit: 'cover'}} />
      : <Img src={staticFile(still)} style={{width: W, height: H, objectFit: 'cover'}} />}
  </AbsoluteFill>;
}

export function AiLabel() {
  const f = useCurrentFrame();
  if (f >= LABEL_FRAMES) return null;
  const o = interpolate(f, [0, 6, LABEL_FRAMES - 10, LABEL_FRAMES], [0, .55, .55, 0], {extrapolateRight: 'clamp'});
  return <div data-ai-label style={{position: 'absolute', left: SAFE, top: SAFE, fontFamily: FONT, fontWeight: 600,
    fontSize: 22, lineHeight: '28px', color: '#fff', opacity: o, background: 'rgba(0,0,0,.35)', padding: '2px 10px',
    borderRadius: 8}}>Hình ảnh tạo bởi AI</div>;
}

function Progress({total}) {
  const f = useCurrentFrame();
  return <div style={{position: 'absolute', left: 0, top: 0, height: 10, width: `${(f / total) * 100}%`,
    background: 'linear-gradient(90deg,#ffd166,#ef476f)'}} />;
}

function StepCard({n, total, text}) {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f - 3, fps, config: {damping: 13, stiffness: 170}});
  return <>
    <div style={{position: 'absolute', right: SAFE, top: SAFE, transform: `scale(${k})`, transformOrigin: '100% 0',
      fontFamily: FONT, fontWeight: 900, fontSize: 40, color: '#1d1d1d', background: '#ffd166', padding: '10px 22px',
      borderRadius: 18, boxShadow: '0 8px 0 rgba(0,0,0,.25)'}}>BƯỚC {n}/{total}</div>
    <div style={{position: 'absolute', left: SAFE, right: SAFE, bottom: BOTTOM, transform: `translateY(${(1 - k) * 60}px)`,
      opacity: k, fontFamily: FONT, fontWeight: 800, fontSize: 56, lineHeight: 1.2, color: '#fff', textAlign: 'center',
      background: 'rgba(15,15,15,.72)', padding: '24px 28px', borderRadius: 30, border: '4px solid rgba(255,255,255,.85)',
      overflowWrap: 'anywhere'}}>{text}</div>
  </>;
}

function Hook({title, img}) {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f, fps, config: {damping: 12}});
  return <AbsoluteFill>
    <KenBurns src={img} dur={HOOK} variant={1} />
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 45%)'}} />
    <div style={{position: 'absolute', left: SAFE, right: SAFE, top: 200, transform: `scale(${.7 + .3 * k})`, opacity: k,
      fontFamily: FONT, fontWeight: 900, fontSize: 74, lineHeight: 1.15, color: '#fff', textAlign: 'center',
      WebkitTextStroke: '3px #111', paintOrder: 'stroke fill', textShadow: '0 8px 24px rgba(0,0,0,.6)',
      overflowWrap: 'anywhere'}}>{title}</div>
  </AbsoluteFill>;
}

function EndCard({img, materials, hasLinks}) {
  const f = useCurrentFrame();
  return <AbsoluteFill>
    <KenBurns src={img} dur={END} blur={18} />
    <div style={{position: 'absolute', left: SAFE, right: SAFE, top: 220, fontFamily: FONT, color: '#fff'}}>
      <div style={{fontWeight: 900, fontSize: 62, marginBottom: 26}}>Bạn cần chuẩn bị:</div>
      {materials.slice(0, 8).map((m, i) => <div key={i} style={{fontWeight: 700, fontSize: 40, lineHeight: 1.35,
        opacity: interpolate(f, [4 + i * 3, 10 + i * 3], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        • {m.name}{m.qty ? ` — ${m.qty}` : ''}</div>)}
      <div style={{marginTop: 36, fontWeight: 900, fontSize: 52, color: '#ffd166'}}>
        {hasLinks ? 'Đồ dùng trong video 👉 link ở bio' : 'Lưu lại để làm theo nhé! 💾'}</div>
    </div>
  </AbsoluteFill>;
}

function Fade({children, T}) {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{opacity: interpolate(f, [0, T], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{children}</AbsoluteFill>;
}

export function DiyVideo({guide}) {
  const n = guide.steps.length, S = stepFrames(n), total = totalFrames(n);
  return <AbsoluteFill style={{background: '#000'}}>
    <Sequence durationInFrames={HOOK}><Hook title={guide.title} img={guide.hook} /></Sequence>
    {guide.steps.map((s, i) => <Sequence key={i} from={HOOK + i * S} durationInFrames={S + (i < n - 1 ? XFADE : 0)}>
      <Fade T={XFADE}>
        {s.clip ? <KeyClip clip={s.clip} still={s.image} dur={S} /> : <KenBurns src={s.image} dur={S + XFADE} variant={i} />}
        <StepCard n={s.n} total={n} text={s.on_screen} />
      </Fade>
    </Sequence>)}
    <Sequence from={HOOK + n * S} durationInFrames={END}>
      <EndCard img={guide.hook} materials={guide.materials} hasLinks={!!guide.hasLinks} /></Sequence>
    <Progress total={total} />
    <AiLabel />
    <Audio src={staticFile('audio/music.wav')} volume={(f) => interpolate(f, [0, 10, total - 20, total], [0, .35, .35, 0],
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
    <Sfx at={0} name="sparkle" />
    {guide.steps.map((_, i) => <Sfx key={i} at={HOOK + i * S} name={i % 2 ? 'whoosh' : 'pop'} />)}
    <Sfx at={HOOK + n * S} name="ding" />
  </AbsoluteFill>;
}
