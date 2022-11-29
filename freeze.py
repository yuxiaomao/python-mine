# Build standalone executable for Windows

from py2exe import freeze

freeze(windows=['mine.py'],
       options={'bundle_files': 1, # As we use only Python standard library
                'compressed': True},
       version_info={'copyright': "Yuxiao Mao",
                     'version': "1.0.0",
                     'product_name': "Minesweeper",
                     "product_version": "1.0.0"}
       )