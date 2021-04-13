from distutils.core import setup
import setup_translate

pkg = 'Extensions.SDGRadio'
setup (name='enigma2-plugin-extensions-sdgradio',
       version='2.0',
       description='Enigma2 Software Defined Radio',
       package_dir={pkg: 'plugin'},
       packages=[pkg],
       package_data={pkg: ['*.xml', '*.png', 'fonts/*.ttf', 'img/*.png']},
       cmdclass=setup_translate.cmdclass,
)
