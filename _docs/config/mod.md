---
title: Mod Config
category: Config
---


The mod config (descent.ini) houses all the settings for the mod half of the Decision Descent.
> Relevant settings in this config will be sent to the mod


### Core Settings 
* **maximum_polls** --- ***integer***<br/>
   The maximum number of polls that can be running at once.<br/>
   If this is -1, an infinite amount of polls will be allowed.<br/>
   If this is 0, the mod will not conduct any polls.
   
   
* **maximum_choices** --- ***integer***<br/>
    The maximum number of choices a single poll is allowed to have.<br/>
    If this is -1, an infinite amount of choices will be allowed.<br/>
    If this is less than 2, polls are essentially disabled.
    
    
* **duration** --- ***integer***<br/>
    The number of seconds a poll will "run".  When a poll is over, the winning choice will be picked.
    
    
* **delay** --- ***integer***<br/>
    The number of seconds the poll will delay picking a winner for.<br/>
    This essentially has the same effect as increasing the duration by this value.<br/>
    If this value is below 0, the client will attempt to calculate the average viewer delay.<br/>
    While this calculation runs every hour, you can use `!dd calculateDelay` to manually calculate it.


### HUD Settings
* **hud_enabled** --- ***boolean***<br/>
    Whether or not the in-game HUD is enabled.<br/>
    > This is generally disabled in favor of in-stream polls.
    
    
* **font** --- ***string***<br/>
    The font the HUD will use.  This will only work for fonts recognised by Isaac.
    
    
* **text_color** --- ***string***<br/>
    The hex color code to use for the HUD's text.
    
    
* **transparency** --- ***float***<br/>
    The transparency of the HUD's text.
    
    
* **width** --- ***float***<br/>
    The width of the text.
    
    
* **height** --- ***float***<br/>
    The height of the text.
    
    
* **min_x** --- ***integer***<br/>
    The top-left x coordinate of the HUD.
    
    
* **min_y** --- ***integer***<br/>
    The top-left y coordinate of the HUD.
    
    
* **max_x** --- ***integer***<br/>
    The bottom-right x coordinate of the HUD.
    
    
* **max_y** --- ***integer***<br/>
    The bottom-right y coordinate of the HUD.


### HTTP Settings
* **port** --- ***integer***<br/>
    The port to listen on.  If this value is changed, the mod will connect to the default port, 
    broadcast the change to the mod half, then reconnect on the new port.
    
    
### Debug Settings
This section has one lone setting (enabled).  If debug mode is enabled, extract output will be 
inserted into Isaac's log file.  For the client's debug mode, please refer to the [client's config]({{ "config/client" | relative_url }}).
