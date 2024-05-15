# HomeAssistantPlugin for [StreamController](https://github.com/StreamController/StreamController)
Control your Home Assistant instance from your StreamDeck

__This is no official plugin - I have no affiliation with Home Assistant, StreamDeck or StreamController.__

## Prerequisites
* `websocket_api` must be present in your `configuration.yaml`. Remember to restart Home Assistant after updating your configuration.
* You need a _long-lived access token_ to connect to Home Assistant. To create one, go to your user profile and click on the _Security_ tab. All the way at the bottom of the page is a button to create a new token. You can only see/copy the token immediately after creating it. Once you dismiss the dialog, you won't be able to retrieve the token.  
  __Be very careful with your Home Assistant information and your token. If your Home Assistant instance is accessible from the internet, anyone with this information can access and control your Home Assistant instance.__

## Features
* Connect to your Home Assistant instance
* Select a domain and entity
* Option to call a service for the entity either on key down or key up (or both, if you wish to)
* Option to show the entity icon
  * If the entity's state is _on_, the icon is shown in yellow
    * If the entity's state changes, the color is updated on the StreamDeck
  * Scale and opacity of the icon are customizable
  * If the entity is a media player, the icon is instead reflecting the selected service
* Option to show entity state or attribute text
  * If the entity's state changes, the text is updated on the StreamDeck
  * Position and size of the text are customizable
  * Option to show unit of measurement (with or without line break)
* Automatic connection retries when the connection is lost for up to one hour

![Streamdeck UI Usage Example](/assets/action.png)

## Known bugs
* You tell me

## Planned features
* Option to change icon color
* Possibly further custom icons based on domains and services
