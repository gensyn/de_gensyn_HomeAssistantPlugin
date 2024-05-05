# HomeAssistantPlugin for [StreamController](https://github.com/StreamController/StreamController)
Control your Home Assistant instance from your StreamDeck

__This is no official plugin - I have no affiliation with Home Assistant or StreamController.__

## Prerequisites
* `websocket_api` must be present in your `configuration.yaml`. Remember to restart Home Assistant after updating your configuration.
* You need a _long-lived access token_ to connect to Home Assistant. To create one, go to your user profile and click on the _Security_ tab. All the way at the bottom of the page is a button to create a new token. You can only see/copy the token immediately after creating it. Once you dismiss the dialog, you won't be able to retrieve the token.  
  __Be very careful with your Home Assistant information and your token. If your Home Assistant instance is accessible from the internet, anyone with this information can access and control your Home Assistant instance.__

## Features
* Connect to your Home Assistant instance
* Select a domain, entity and service to call that service for the entity either on key down or key up (or both, if you wish to)
* If the entity has an icon, this icon is set as the image for the key
  * If the entity's state is _on_, the icon is shown in yellow
    * If the entity's state changes, the color is updated on the StreamDeck 

![Streamdeck UI Usage Example](/assets/action.png)

## Known bugs
* Reconnect on lost connection to Home Assistant is only triggered when you try to interact with Home Assistant (i.e. send service calls)
  * Automatic reconnects are planned
* Entity IDs are truncated in the drop-down menu
* Icons don't update when Home Assistant settings are changed (they should update on connect)

## Planned features
* Make showing the icon optional
* Option to show entity state/attribute text