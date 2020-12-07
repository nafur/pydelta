import argparse

class _ModularHelpEnabler(argparse.Action):
    """A custom action that enables help for a single argument group."""
    def __call__(self, parser, namespace, values, option_string = None):
        parser.enable_modular_help(self.const)

class ModularArgumentParser(argparse.ArgumentParser):
    """A variant of argparse.ArgumentParser that allows to modularly enable and disable printing help for individual argument groups.
    A new variant of add_argument_groups() allows adding commands of the form --help-group.
    """
    def __init__(self, *args, **kwargs):
        """As argparse.ArgumentParser.__init__(), additionally modular_action_groups = [] can be used to specify the names of argument groups used for the custom help options."""
        self._modular_action_groups = {}
        modular_help_groups = kwargs.pop('modular_help_groups', [])
        super().__init__(*args, **kwargs)
        self._modular_help_groups = {}
        for name in modular_help_groups:
            self._modular_help_groups[name] = self.add_argument_group(name)

    def add_argument_group(self, *args, **kwargs):
        """As argparse.ArgumentParser.add_argument_group(), additionally help_name, help_group and help_text allow to add a new option `--help-{{help_name}}."""
        help_name = kwargs.pop('help_name', None)
        help_group = kwargs.pop('help_group', None)
        help_text = kwargs.pop('help_text', 'show help for {}')
        grp = super().add_argument_group(*args, **kwargs)
        if help_name is not None:
            self._modular_action_groups[grp] = help_name
            parser = self
            if help_group is not None:
                parser = self._modular_help_groups[help_group]
            parser.add_argument('--help-{}'.format(help_name), action=_ModularHelpEnabler, nargs=0, default=False, const=grp, help = help_text.format(help_name))
        return grp
    def enable_modular_help(self, grp):
        """Remove grp from self._modular_action_groups and thereby enable printing it."""
        del self._modular_action_groups[grp]
    def format_help(self):
        """Removes all items from self._action_groups that are still in self._modular_action_groups."""
        self._action_groups = [
            ag for ag in self._action_groups
            if ag not in self._modular_action_groups
        ]
        return super().format_help()
