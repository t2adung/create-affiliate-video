import React from 'react';
import {Composition, registerRoot, continueRender, delayRender} from 'remotion';
import {DiyVideo, totalFrames, FPS} from './diy.jsx';

const handle = delayRender('fonts');
Promise.all(['900 40px "Be Vietnam Pro"', '800 40px "Be Vietnam Pro"', '700 40px "Be Vietnam Pro"', '600 40px "Be Vietnam Pro"']
  .map(f => document.fonts.load(f, 'Bước ưỡ Đ'))).then(() => continueRender(handle));

const sample = {title: 'Demo', steps: [{n: 1, on_screen: 'x', image: 'g/01.jpg'}], materials: [], hook: 'g/01.jpg'};

function Root() {
  return <Composition id="DIY" component={DiyVideo} width={1080} height={1920} fps={FPS} durationInFrames={300}
    defaultProps={{guide: sample}}
    calculateMetadata={({props}) => ({durationInFrames: totalFrames(props.guide.steps.length)})} />;
}
registerRoot(Root);
