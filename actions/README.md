# HomeAssistantPlugin for [StreamController](https://github.com/StreamController/StreamController)
## Control your Home Assistant instance from your StreamDeck

### Features
* Connect to your Home Assistant instance
* Select a domain, an entity and a service to call the service for the entity either on key down or key up (or both, if you wish to)
* If the entity has an icon, this icon is set as the image for the key
  * If the entity's state is _on_, the icon is shown in yellow
    * If the entity's state changes, the color is updated on the StreamDeck 

![Streamdeck UI Usage Example](/assets/action.png)

### Known bugs
* Reconnect on lost connection to Home Assistant is only triggered when you try to interact with Home Assistant (i.e. send service calls)
  * Automatic reconnects are planned
* Entity IDs are truncated in the drop-down menu