---
title: Message Format
category: API
---

This page serves as a reference to the format of the JSON messages sent to an from the duo.


|  Key   |   Type   | Description                                                                                                                                                                             |
|--------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| sender | int      | An enum value representing the sender.  If this value is 0, the message originated from the client.  If this value is 1, the message originated from the mod.                           |
| intent | str      | A string representing the intent of the message.  The intent is a namespace that points to a callable on the other side.  This callable is called with the specified arguments.         |
| args   | list     | A list of translated arguments to pass to the intent callable.                                                                                                                          |
| kwargs | object   | A key:value object with translated values.                                                                                                                                              |
| reply  | str/null | A string representing the intent of reply message.  The intent is a namespace that points to a callable on the sending side.  This callable is called with the intent's response(s)     |