from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import os
from string import Template

from mb.lib import logger


class TemplateEngine(object):
    def __init__(self):
        self.log = logger.get_logger('[TemplateEngine]')
        self.log.debug('Initializing {0}'.format(self.__class__.__name__))
        return

    def generate_files(self):
        self.log.info('Generating templated files...')
        return self._generate_files()

    @abc.abstractmethod
    def _generate_files(self):
        raise NotImplementedError("'_generate_files' must be reimplemented by %s" % self)


class DefaultTemplateEngine(TemplateEngine):
    def __init__(self, build_context, config):
        super(DefaultTemplateEngine, self).__init__()
        self.build_context = build_context
        self.config = config

    def _generate_file_from_tmpl(self, build_tmpl_dir, template_file, variables):
        template_file_contents = ""

        with open(os.path.join(build_tmpl_dir, template_file), 'r') as file:
            first_line = file.readline().strip()

        if '# build-template' not in first_line:
            self.log.debug('The following file is being ignored: {0}'.format(template_file))
            return

        split_first_line = first_line.split('|')
        if len(split_first_line) > 1:
            dest_dir_name = os.path.dirname(split_first_line[1])
            if not os.path.exists(dest_dir_name):
                os.makedirs(dest_dir_name)
            dest_file = os.path.join(self.config.project_dir, split_first_line[1])
        else:
            dest_file = os.path.join(self.config.project_dir, template_file)

        with open(os.path.join(build_tmpl_dir, template_file), 'r') as file:
            template_file_contents = file.read()

        template = Template(template_file_contents)
        new_file_contents = template.safe_substitute(variables)

        with open(dest_file, 'w') as file:
            file.write(new_file_contents)

    def _generate_files(self):
        variables = {}
        variables.update(self.config.variables)
        variables.update(self.build_context.variables)

        if not os.path.isdir(self.config.template_dir):
            self.log.warn('There are no template files to generate!')
            return

        for file in os.listdir(self.config.template_dir):
            self._generate_file_from_tmpl(self.config.template_dir, file, variables)
