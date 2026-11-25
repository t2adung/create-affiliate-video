import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Composition, registerRoot, useVideoConfig} from 'remotion';

function TitleCard({title, subtitle}) {
  const text = useRef(null);
  const {width, height} = useVideoConfig();
  useLayoutEffect(() => {
    const parent = text.current.parentElement.getBoundingClientRect();
    const range = document.createRange();
    range.selectNodeContents(text.current);
    const overflow = Array.from(range.getClientRects()).find(bounds =>
      bounds.left < parent.left + 47 || bounds.right > parent.right - 47 ||
      bounds.top < parent.top + 47 || bounds.bottom > parent.bottom - 47);
    if (overflow) {
      throw new Error('Text extends beyond the safe area ' + JSON.stringify([parent, overflow]));
    }
  }, [title, subtitle, width, height]);
  return (
    <AbsoluteFill style={{
      background: '#102a43', color: 'white', fontFamily: 'sans-serif',
      justifyContent: 'center', alignItems: 'center', padding: 48,
      width, height, boxSizing: 'border-box', textAlign: 'center', overflowWrap: 'anywhere',
    }}>
      <div ref={text} style={{display: 'grid', gap: 16, width: '100%', minWidth: 0}}>
        <div style={{fontSize: 36, fontWeight: 700}}>{title}</div>
        <div style={{fontSize: 20}}>{subtitle}</div>
      </div>
    </AbsoluteFill>
  );
}

function Root() {
  return <Composition id="TitleCard" component={TitleCard} width={640}
    height={360} fps={24} durationInFrames={24}
    defaultProps={{title: 'Water cycle', subtitle: 'A synthetic lesson'}} />;
}

registerRoot(Root);
