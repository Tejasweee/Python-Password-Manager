import sys

def installer(package):
    print('Installing..', package)
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    import cryptography
    print('Cryptography is already installed...')
except ImportError:
    installer('cryptography')

print('All requirements satisfied...')
