# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import unittest

print "-" * 80
print "Start pre-build testing"
print "-" * 80

#Make sure all the tests complete.
import tests
loader = unittest.TestLoader()
result = unittest.TestResult()
suite = loader.loadTestsFromModule(tests)
suite.run(result)
if not result.wasSuccessful():
    print "Unit tests have failed!"
    for l in result.errors, result.failures:
        for case, error in l:
            print "-" * 80
            desc = case.shortDescription()
            if desc:
                print desc
            print error        
    print '''If you see an error like: "'ascii' codec can't encode character...", see\nthe Beautiful Soup documentation:\n http://www.crummy.com/software/BeautifulSoup/documentation.html#Why%20can't%20Beautiful%20Soup%20print%20out%20the%20non-ASCII%20characters%20I%20gave%20it?'''
    print "This might or might not be a problem depending on what you plan to do with\nBeautiful Soup."
    if sys.argv[1] == 'sdist':
        print
        print "I'm not going to make a source distribution since the tests don't pass."
        sys.exit(1)

print "-" * 80
print "All tests passed"
print "-" * 80
setup(
    name='wsdl2soaplib',
    version='0.1.0',
    author=u'Francisco José Marques Vieira',
    author_email='francisco.j.m.vieira@gmail.com',
    py_modules=['wsdl2soaplib',],
    entry_points = {
    'console_scripts': [
        'wsdl2soaplib = wsdl2soaplib:main',
        ],
    },
    
    #scripts=['wsdl2soaplib.py',],
    url='http://pypi.python.org/pypi/wsdl2soaplib/',
    license='LICENSE',
    description='Generate python soaplib stubs from wsdl',
    long_description=open('README').read(),
    install_requires=[
        "suds == 0.4.1",
        "soaplib >= 2.0.0-beta",
    ],
)
