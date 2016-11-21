from distutils.core import setup

pkg = 'Extensions.SDGRadio'
setup (name = 'enigma2-plugin-extensions-sdgradio',
       version = '1.0',
       description = 'Enigma2 Software Defined Radio',
       package_dir = {pkg: 'plugin'},
       packages = [pkg],
       package_data = {pkg: ['fonts/*.ttf', 'img/*.png']},
      )

