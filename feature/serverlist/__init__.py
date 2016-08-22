__author__ = 'syx'


import ansible.runner

runner = ansible.runner.Runner(
   module_name='setup',
   module_args='',
   pattern='web*',
   forks=10
)
datastructure = runner.run()
print datastructure