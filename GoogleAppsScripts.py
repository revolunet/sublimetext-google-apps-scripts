# -*- encoding: UTF-8 -*-

"""
GoogleAppsScripts.py - https://github.com/revolunet/sublimetext-google-apps-scripts
copyright: (c) 2013 by Julien Bouquillon - julien@revolunet.com
license: MIT
"""

import sys
import os
# force include 3rd party libs
LIBS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
sys.path.insert(0, LIBS_PATH)

import sublime
import sublime_plugin
import ScriptsBrowser
import SublimeHelper
#import desktop

# for debug only
# reload(ScriptsBrowser)
# reload(SublimeHelper)


def oauth_ask_token_flow(auth_url, callback):
    ''' present the url to user and an input to paste the oauth token '''
    SublimeHelper.message('Open the URL below in your browser then paste the oauth code in the input box at this window bottom : %s' % auth_url)
    #SublimeHelper.message('Authorize access in the opened webpage then paste the oauth code at the bottom of this window')
    #desktop.open(auth_url)
    def finished(code):
        result = callback(code)
        if not result:
            SublimeHelper.message("invalid OAuth code, try again :/")
        else:
            SublimeHelper.message("Authentification success. try again please")
        return result
    SublimeHelper.show_input("Oauth code : ", "", finished)


def auth_user(force=False):
    ''' auth user using sublime dialogs '''
    browser = get_GoogleAppsScriptsBrowser()
    browser.login(force=force)


def get_GoogleAppsScriptsBrowser():
    ''' instantiate GoogleAppsScriptsBrowser with some fixed settings for oauth '''
    settings = sublime.load_settings('SublimeGoogleAppsScripts.sublime-settings')
    storage_file = settings.get('oauth_credentials_storage')
    if storage_file:
        storage_file = os.path.join(sublime.packages_path(), 'SublimeGoogleAppsScripts', storage_file)
    browser = ScriptsBrowser.GoogleAppsScriptsBrowser(client_id=settings.get('oauth_client_id'), client_secret=settings.get('oauth_client_secret'), creds_storage=storage_file)
    browser.set_token_flow_callback(oauth_ask_token_flow)
    browser.login()
    return browser


class GoogleAppsScriptsListener(sublime_plugin.EventListener):
    ''' listen on_post_save to save changes back to google drive '''
    def on_post_save(self, view):
        ''' retrieve the full project data and update this file source only '''
        project_id = view.settings().get('GoogleAppsScripts-project')
        file_id = view.settings().get('GoogleAppsScripts-file')
        if file_id:
            region = sublime.Region(0, view.size())
            contents = view.substr(region)
            self.browser = get_GoogleAppsScriptsBrowser()
            if self.browser.update_file(project_id, file_id, contents):
                SublimeHelper.message('File saved to Google Drive')
            else:
                SublimeHelper.message('Error saving file; check the ST console')



class GoogleAppsScriptsAuthCommand(sublime_plugin.TextCommand):
    ''' launch oauth process only '''
    def run(self, edit):
        auth_user(force=True)


class GoogleAppsScriptsCommand(sublime_plugin.TextCommand):
    ''' main plugin code, handle sublime menus and call to other classes '''
    def __init__(self, view):
        super(GoogleAppsScriptsCommand, self).__init__(view)
        self.browser = None
        # just cache projects
        self.projects = {}

    def get_projects(self):
        return self.projects

    def update_projects(self):
        projects = self.browser.projects()
        self.projects = dict([(project.get('id'), project) for project in projects])

    def run(self, edit):
        self.browser = get_GoogleAppsScriptsBrowser()
        if not self.browser.token:
            #SublimeHelper.message('Please login and try again')
            return
        self.update_projects()
        if not self.projects:
            SublimeHelper.message('Cannot fetch projects, or no project found')
            return
        self.prompt_projects()

    def prompt_projects(self):
        projects_list = [project.get('title') for project in self.get_projects().values()]
        projects_list.insert(0, ['New project', 'creates a new scripts project'])
        SublimeHelper.show_list_panel(projects_list, self.project_selected)

    def get_full_filename(self, file):
        if file.get('type')=='server_js':
            return '%s.js' % file.get('name')
        elif file.get('type')=='html':
            return '%s.html' % file.get('name')
        return file.get('name')

    def prompt_files(self, project):
        files = self.browser.files(project.get('id'))
        files_list = [self.get_full_filename(file) for file in files]
        files_list.insert(0, ['Back to projects', 'Back to project list'])
        files_list.insert(1, ['New file', 'creates a new script in the project %s' % project.get('title')])

        def callback(index):
            self.file_selected(index, files, project)

        SublimeHelper.show_list_panel(files_list, callback)

    def file_selected(self, index, items, project):
        if index == 0:
            # back to projects
            self.prompt_projects()
        elif index == 1:
            # new file
            # update file ref inside project
            # TODO: POST new file
            pass
        else:
            selected_file = items[index - 2]
            # write locally and open it
            path = SublimeHelper.write(selected_file.get('source'), name=self.get_full_filename(selected_file))
            new_view = SublimeHelper.get_window().open_file(path)
            if selected_file.get('type')=='server_js':
                new_view.set_syntax_file('Packages/Javascript/Javascript.tmLanguage')
            elif selected_file.get('type')=='html':
                new_view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
            new_view.settings().set('GoogleAppsScripts-project', project.get('id'))
            new_view.settings().set('GoogleAppsScripts-file', selected_file.get('id'))

    def project_selected(self, index):
        print 'project_selected', index
        if index == -1:
            pass
        elif index == 0:
            # new project
            pass
        else:
            index -= 1
            project = self.get_projects().values()[index]
         #   print 'selected', project
            self.prompt_files(project)
