primary embed:

```html

<script src="https://labourreforms.uk/lliframe2024/embed.js"></script>

```

fallback embed:

```html 

<script type="text/javascript">
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
</script>
<iframe
  id="labourreforms-iframe"
  src="https://labourreforms.uk/lliframe2024/"
  frameborder="0"
  title="Labour Reforms"
  sandbox="allow-same-origin allow-scripts"
  style="width: 100%; height: 1000px;"
></iframe>
```
