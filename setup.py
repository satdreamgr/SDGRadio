from distutils.core import setup

pkg = 'Enigma2 Software Defined Radio'
setup (name = 'enigma2-plugin-extensions-sdgradio',
       version = '1.0',
       description = 'Enigma2 Software Defined Radio',
       package_dir = {pkg: 'plugin'},
       packages = [pkg],
       package_data = {pkg: ['fonts/*.ttf', 'img/*.png']},
      )

