#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab

import logging
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from openvpn3_indicator.about import APPLICATION_ID
from openvpn3_indicator.dialogs.credentials import construct_credentials_dialog, CredentialsUserInput

# name, mask, value, can_store, and the field we expect to end up focused.
# '' means there's a saved value that's just empty. None means nothing was ever saved.
# OTP is never saved, so it's always None.
FOCUS_SCENARIOS = [
    ('nothing stored', [
        CredentialsUserInput('Username', False, None, True),
        CredentialsUserInput('Password', True, None, True),
        CredentialsUserInput('OTP', True, None, False),
    ], 'Username'),
    ('username stored only', [
        CredentialsUserInput('Username', False, 'user', True),
        CredentialsUserInput('Password', True, '', True),
        CredentialsUserInput('OTP', True, None, False),
    ], 'Password'),
    ('password stored only', [
        CredentialsUserInput('Username', False, '', True),
        CredentialsUserInput('Password', True, 'secret', True),
        CredentialsUserInput('OTP', True, None, False),
    ], 'Username'),
    ('username and password stored', [
        CredentialsUserInput('Username', False, 'user', True),
        CredentialsUserInput('Password', True, 'secret', True),
        CredentialsUserInput('OTP', True, None, False),
    ], 'OTP'),
]


def focused_field_label(dialog):
    focused = dialog.get_focus()
    grid = next((child for child in dialog.get_content_area().get_children()
                 if isinstance(child, Gtk.Grid)), None)
    if not isinstance(focused, Gtk.Entry) or grid is None:
        return None
    row = grid.child_get_property(focused, 'top-attach')
    for child in grid.get_children():
        if (isinstance(child, Gtk.Label)
                and grid.child_get_property(child, 'left-attach') == 0
                and grid.child_get_property(child, 'top-attach') == row):
            return child.get_text()
    return None


def verify_focus():
    for name, user_inputs, expected in FOCUS_SCENARIOS:
        dialog = construct_credentials_dialog(name, user_inputs)
        while Gtk.events_pending():  # realize widgets so the focus is applied
            Gtk.main_iteration_do(False)
        got = focused_field_label(dialog)
        print(f"[{'PASS' if got == expected else 'FAIL'}] {name}: focus on {got!r} (expected {expected!r})")
        dialog.destroy()


class Test(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self,
            application_id=APPLICATION_ID,
            )
        self.connect('startup', self.on_startup)
        self.connect('activate', self.on_activate)

    def on_activate(self, *args, **kwargs):
        pass
    def on_startup(self, *args, **kwargs):
        self.hold()

        verify_focus()

        user_inputs = [
                CredentialsUserInput(name='Username', mask=False, value='user', can_store=True),
                CredentialsUserInput(name='Password', mask=True, value=None, can_store=True),
                CredentialsUserInput(name='Other', mask=True, value='rehto', can_store=True),
                ]

        dialog = construct_credentials_dialog('Test', user_inputs, on_connect=self.action_connect, on_cancel=self.action_quit)
        dialog.set_visible(True)

        GLib.timeout_add(1000, self.on_schedule)
        GLib.timeout_add(60000, self.action_quit)

    def on_schedule(self, *args, **kwargs):
        GLib.timeout_add(1000, self.on_schedule)

    def action_connect(self, user_inputs, store):
        print(f'Result: {dict([(ui.name, ui.value) for ui in user_inputs])}, Store: {store}')
        self.action_quit()

    def action_quit(self, *args, **kwargs):
        self.release()

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    test = Test()
    test.run(sys.argv)
