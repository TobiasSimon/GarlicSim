#!/usr/bin/env python

import os
import sys
import re
import shutil

import pkg_resources

import simpack_template
simpack_template_module_name = simpack_template.__name__


def start_simpack(containing_folder, name):
    """
    
    """
    
    if not re.search(r'^[_a-zA-Z]\w*$', name): # If it's not a valid directory name.
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise Exception("%r is not a valid simpack name. Please %s." % (name, app_or_project, message))
    folder = os.path.join(containing_folder, name)
    
    os.mkdir(folder)

    CODE A WALK IN PKG_RESOURCES
    
    # Determine where the app or project templates are. Use
    # django.__path__[0] because we don't know into which directory
    # django has been installed.
    template_dir = os.path.join(django.__path__[0], 'conf', '%s_template' % app_or_project)

    for d, subdirs, files in os.walk(template_dir):
        relative_dir = d[len(template_dir)+1:].replace('%s_name' % app_or_project, name)
        if relative_dir:
            os.mkdir(os.path.join(top_dir, relative_dir))
        for i, subdir in enumerate(subdirs):
            if subdir.startswith('.'):
                del subdirs[i]
        for f in files:
            if not f.endswith('.py'):
                # Ignore .pyc, .pyo, .py.class etc, as they cause various
                # breakages.
                continue
            path_old = os.path.join(d, f)
            path_new = os.path.join(top_dir, relative_dir, f.replace('%s_name' % app_or_project, name))
            fp_old = open(path_old, 'r')
            fp_new = open(path_new, 'w')
            fp_new.write(fp_old.read().replace('{{ %s_name }}' % app_or_project, name).replace('{{ %s_name }}' % other, other_name))
            fp_old.close()
            fp_new.close()
            try:
                shutil.copymode(path_old, path_new)
                _make_writeable(path_new)
            except OSError:
                sys.stderr.write(style.NOTICE("Notice: Couldn't set permission bits on %s. You're probably using an uncommon filesystem setup. No problem.\n" % path_new))

                
def _make_writeable(filename):
    """
    Make sure that the file is writeable. Useful if our source is
    read-only.
    
    """
    import stat
    if sys.platform.startswith('java'):
        # On Jython there is no os.access()
        return
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)

        
def show_help():
    '''tododoc'''
    
if __name__ == '__main__':

    if len(sys.argv) != 2:
        show_help()
        sys.exit()
    arg = sys.argv[1]

    if arg == '--help':
        show_help()
        sys.exit()
    
    start_simpack(os.curdir, arg)
    
        