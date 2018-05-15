---
title: Client Config
category: Config
---

The client config (settings.ini) houses all the settings for the client half of Decision Descent.
> Relevant settings in this config will be sent to the mod


### Location Settings
* **integrations** --- ***string***<br/>
    A directory path where integrations will be loaded.
    
    
* **configs** --- ***str***<br/>
    A directory path where configs will be stored.


### Debug Settings
This section has one lone setting (enabled).  If debug mode is enabled, extract output will be 
inserted into the client's log file.  For the mod's debug mode, please refer to the [mod's config]({{ "config/mod" | relative_url }}).
