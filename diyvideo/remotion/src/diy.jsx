import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, Audio, interpolate, spring, staticFile, useCurrentFrame,
  useVideoConfig, Easing} from 'remotion';
import '@fontsource/be-vietnam-pro/600.css';
import '@fontsource/be-vietnam-pro/700.css';
import '@fontsource/be-vietnam-pro/800.css';
import '@fontsource/be-vietnam-pro/900.css';

export const FPS = 30, W = 1080, H = 1920, LABEL_FRAMES = 3 * FPS;
const DEFAULT_T = (n) => ({hook: 60, mats: 0, step: Math.round(Math.min(3.0, 25 / n) * FPS), end: 90, xfade: 8, zoom: 0.08});
export const timingOf = (g) => g.timing || DEFAULT_T(g.steps.length);
export const totalFrames = (g) => { const t = timingOf(g); return t.hook + t.mats + g.steps.length * t.step + t.end; };
const SAFE = 60, BOTTOM = 320;
const FONT = "'Be Vietnam Pro', 'Noto Color Emoji', sans-serif";

function Sfx({at, name, volume = 0.5}) {
  return <Sequence from={at} layout="none"><Audio src={staticFile(`audio/${name}.wav`)} volume={volume} /></Sequence>;
}

function KenBurns({src, dur, variant = 0, blur = 0, zoom = 0.08}) {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, dur], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
  const z = zoom, m = zoom * 250;
  const moves = [[1.0, 1 + z, 0, -m], [1 + z, 1.0, m * .7, m * .4], [1.0, 1 + z, -m * .8, 0], [1 + z, 1.0, 0, m]];
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

function StepCard({n, total, text, compact}) {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f - 3, fps, config: {damping: 13, stiffness: 170}});
  if (compact) {
    return <div style={{position: 'absolute', left: SAFE, right: SAFE, bottom: BOTTOM, display: 'flex', justifyContent: 'center',
      opacity: k, transform: `translateY(${(1 - k) * 30}px)`}}>
      <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 40, lineHeight: 1.2, color: '#fff', textAlign: 'center',
        background: 'rgba(20,20,20,.55)', padding: '12px 22px', borderRadius: 22, maxWidth: '100%', overflowWrap: 'anywhere'}}>
        {n > 0 ? <><span style={{color: '#ffd166'}}>{n}/{total}</span>&nbsp;&nbsp;</> : null}{text}</div></div>;
  }
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

function Hook({title, img, dur}) {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f, fps, config: {damping: 12}});
  return <AbsoluteFill>
    <KenBurns src={img} dur={dur} variant={1} zoom={0.04} />
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 45%)'}} />
    <div style={{position: 'absolute', left: SAFE, right: SAFE, top: 200, transform: `scale(${.7 + .3 * k})`, opacity: k,
      fontFamily: FONT, fontWeight: 900, fontSize: 74, lineHeight: 1.15, color: '#fff', textAlign: 'center',
      WebkitTextStroke: '3px #111', paintOrder: 'stroke fill', textShadow: '0 8px 24px rgba(0,0,0,.6)',
      overflowWrap: 'anywhere'}}>{title}</div>
  </AbsoluteFill>;
}

function EndCard({img, materials, hasLinks, dur}) {
  const f = useCurrentFrame();
  return <AbsoluteFill>
    <KenBurns src={img} dur={dur} blur={18} />
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
  const o = T > 0 ? interpolate(f, [0, T], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
}

export function DiyVideo({guide}) {
  const n = guide.steps.length, t = timingOf(guide), total = totalFrames(guide), S = t.step, X = t.xfade;
  const base = t.hook + t.mats;
  return <AbsoluteFill style={{background: '#000'}}>
    <Sequence durationInFrames={t.hook + (t.mats ? X : 0)}><Fade T={0}><Hook title={guide.title} img={guide.hook} dur={t.hook} /></Fade></Sequence>
    {t.mats > 0 && guide.mats ? <Sequence from={t.hook} durationInFrames={t.mats + X}><Fade T={X}>
      <KenBurns src={guide.mats} dur={t.mats + X} variant={2} zoom={t.zoom} />
      {guide.compact ? <StepCard n={0} total={n} text="Chuẩn bị" compact /> : null}</Fade></Sequence> : null}
    {guide.steps.map((s, i) => <Sequence key={i} from={base + i * S} durationInFrames={S + (i < n - 1 ? X : 0)}>
      <Fade T={X}>
        {s.clip ? <KeyClip clip={s.clip} still={s.image} dur={S} /> : <KenBurns src={s.image} dur={S + X} variant={i} zoom={t.zoom} />}
        <StepCard n={s.n} total={n} text={s.on_screen} compact={guide.compact} />
      </Fade>
    </Sequence>)}
    <Sequence from={base + n * S} durationInFrames={t.end}>
      <Fade T={X}><EndCard img={guide.hook} materials={guide.materials} hasLinks={!!guide.hasLinks} dur={t.end} /></Fade></Sequence>
    <Progress total={total} />
    <AiLabel />
    <Audio src={staticFile('audio/music.wav')} volume={(f) => interpolate(f, [0, 10, total - 20, total], [0, .35, .35, 0],
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
    <Sfx at={0} name="sparkle" />
    {guide.steps.map((_, i) => <Sfx key={i} at={base + i * S} name={i % 2 ? 'whoosh' : 'pop'} volume={guide.compact ? 0.25 : 0.5} />)}
    <Sfx at={base + n * S} name="ding" />
  </AbsoluteFill>;
}
