from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

def fmt_dictionary(m, f, *ks):
    vs = [ m[k] for k in ks ]
    return f.format(*vs)

class FilterModule(object):
    '''Custom filters for working with dictionaries.'''

    def filters(self):
        return {
            'format_dictionary': fmt_dictionary
        }

# ---- Ansible filters ----
