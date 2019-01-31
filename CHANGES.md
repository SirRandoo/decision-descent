# Decision Descent v0.4.0

* Client now properly calls its quit method instead of the application's exit method.
* Fixed Alt+F4 not being a valid shortcut for the quit action.
* Added support for QtUtilities' new settings dialog.
* Tied polls now choose a random choice.
* Devil polls now take extra lives into account.
    * [Known Bug]: All items are given to the player before the death animation finishes.
* Devil polls now take items that grant health into account.
* Devil polls now take bone hearts into account.
* Devil polls now properly grant all awarded items.
* Transformed `Decision Descent.py` into `__main__.py`.
* Added application metadata to the QApplication instance.
* Recoded several components.
* Removed pre-generated UI files.
* Removed system tray support.
* Help→About in the menubar now displays a generated about dialog.
* Client position & size now persists through sessions.
* `client.log` is now dynamically set from the application's metadata.
* Completely restructured the client side
* Fixed the client's log display not properly outputting messages.


# Decision Descent v0.3.0

* Cleaned up global variables in the mod half.
* Support for filtering the client's log output.
* Fixed the client using the built-in formatter instead of our own.
* Added ALT+F4 as a shortcut for closing the client.
* Cleaned up unused code.
* Removed logger check in `setup_logger`.
* Removed left over todo comments.
* Removed unused imports.
* The mod now reconnects to the client if it gets disconnected.
* The client's twitch extension now reconnects when Twitch issues a RECONNECT notice.
* The client now sends the mod Isaac's width and height periodically.
* Removed settings pertaining to positioning the display text in-game.
* The display text in-game is now centered at the bottom of the screen.
* Boss room pedestals are now removed.
* Moved widgets.settings.Settings to QtUtilities.


# Decision Descent v0.2.0

* Temporarily disabled support for Boss Rush polls.
* Properly handles connections --- The client can now only have one Isaac connected to it.
* Decision Descent can now be installed via an installer.
* Curse rooms have a chance of creating a poll.
* Error rooms now have a chance of being devil polls.
* Removed config options pertaining to the HUD's font.
* The client no longer tries to load \_\_pycache\_\_ directories.
* The client now includes the Isaac log's output.  --- The Isaac log is updated twice a second.
* The client now deletes polls from a previous game.
* The client now sends Isaac's config settings.
* The client's menubar now properly shows its menus.
* Items are now removed from item pools after being given.
* Polls are now not generated on levels they shouldn't be.
* Devil polls now properly remove health from the player.
* Devil polls now ensure the player will survive being given an item.


# Decision Descent v0.1.0

* Initial Release
