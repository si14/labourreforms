const labourReformsHandleReceiveMessage = (event) => {
  const eventName = event?.data['eventName'];
  const payload = event?.data['payload'];

  if (!(eventName && payload)) {
    return;
  }

  if (eventName === 'SET_HEIGHT' && payload['height']) {
    const currentIFrameHeight = payload['height'];

    const iframe = document.querySelector('#labourreforms-iframe');
    iframe.style.height = `${currentIFrameHeight}px`;
  }
};

window.addEventListener('message', labourReformsHandleReceiveMessage);

const labourReformsIframeUrl = document.currentScript.src.replace('embed.js', '');

document.currentScript.insertAdjacentHTML('afterend', '<iframe\n' +
  '  id="labourreforms-iframe"\n' +
  `  src="${labourReformsIframeUrl}"\n` +
  '  frameborder="0"\n' +
  '  title="Labour Reforms"\n' +
  '  sandbox="allow-same-origin allow-scripts allow-popups"\n' +
  '  style="width: 100%; height: 1000px;"\n' +
  '></iframe>');