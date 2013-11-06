# sublimetext-google-apps-scripts

Google Apps Scripts offer developers many powerful features like scripting the google web applications (Gmail, google docs...) but the online IDE can be quite frustrating. For this reason, i made this small SublimeText 2 plugin to edit your Google Apps Scripts directly from your preferred editor :)

At the moment it only supports ST2 but ST3 will land soon.

Proudly brought to you by the [revolunet][1] team.

FYI, the same kind of plugin exists for Eclipse and its called [Total Eclipse][2].

## Usage

Just open your palette with `CMD+MAJ+P` then 'Google Apps Scrips : browser projects' to browse and edit your remote scripts :)

## How does it work ?

The plugin uses Google OAuth2 to authenticate yourself and access your projects and scripts with the [scripts Import/Export API][0]. The first time you use the plugin, you'll be asked to provide an OAuth token. It will then be stored (configurable) in the plugin directory.


## Features

 - Google OAuth2 authentification
 - Browse projects and scripts
 - Edit scripts at last :)

## Todo

 - Improve initial OAuth process
 - Add new script
 - Add new project
 - ST3 compatibility

## Licence

Licensed under MIT.

 [0]: https://developers.google.com/apps-script/import-export
 [1]: https://github.com/revolunet
 [2]: http://googledevelopers.blogspot.fr/2013/10/total-eclipse-of-apps-script.html
