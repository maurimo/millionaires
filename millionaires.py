
# disclaimer: this code was written for testing and self-learning, do
# not use in any serious application, do not expect any serious security!
import socket, sys, logging, hashlib, random, json, sympy, pickle

# global settings - make sure those are consistent
NBITS=32 # increase this is comparing worth with Jeff Bezos or Mark Zuckerberg

# we work modulo this prime
P = (1<<510)+15 # yes it happens to be prime

SECURITY=512

# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
LOG = logging.getLogger(__name__)

# utility - wait for connection on port, or connect to host:port
def interact(info):
    info = info.split(':')

    if len(info) == 1:
        port = int(info[0])
        LOG.info('listening on port %d', port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind( ('localhost', port) )
        sock.listen(1)
        connection, client_address = sock.accept()
        LOG.info('Client connected from %s', client_address)

        return connection

    else:
        host, port = info[0], int(info[1])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        LOG.info('connecting to %s:%d', host, port)
        sock.connect( (host,port) )
        LOG.info('connected!')
        return sock


# compute 'ups', they are values that are bigger than a, and will intercept a bigger value of the other party
# for each i, if the i-th bit is 0, set it to 1 and clear lower bits
def s_up(a, n=NBITS):
    return { (a - (a & ((1<<i)-1))) | (1<<i) for i in range(n) if (a>>i) & 1 == 0 }

# compute 'downs', they are values that are smaller than a, and will intercept a smaller value of the other party
# for each i, if the i-th bit is 1, clear lower bits
def s_down(a, n=NBITS):
    return { (a - (a & ((1<<i)-1))) for i in range(n) if (a>>i) & 1 == 1 }

# random integer of 512 bits
def rand512():
    return random.getrandbits(512)

# return the sha512, as an integer
def sha512(s):
    return int.from_bytes(hashlib.sha512(s.encode()).digest(), byteorder='big')

def hashes(s, n=NBITS):
    return [*(sha512(str(x)) for x in s), *(rand512() for i in range(n-len(s)))]


# compute x^e, b y repeated squaring, modulo p
def modpow(x, e, p=P):
    r, t = ((x % p) if (e & 1) else 1), x
    e >>= 1
    while e:
        t = (t * t) % p
        if e & 1:
            r = (r * t) % p
        e >>= 1
    return r

# compute a number relatively prime to b, that is,
# a number r so that r, b have no common factor
def rand_coprime(b):
    while True:
        r = random.randint(b // 4, b)
        if sympy.gcd(r, b) == 1:
            return r

if len(sys.argv) != 3:
    print('Usage: prog.py number_to_compare [host:]port (if host is specified connect, otherwise listen and wait)')
    sys.exit()
        
val = int(sys.argv[1])
if (val >> NBITS) != 0:
    print('Congratulations, you own many billions, and', NBITS, 'bits are not enough for you!')
    print('You will have to up the NBITS parameter, and the other party too for this to work.')
    sys.exit()

LOG.info('will compare the provided value with a private remote number')

LOG.info('computing my downs/ups, plus padding to hide their sizes')
my_downs = hashes(s_down(val))
my_ups = hashes(s_up(val))

LOG.info('generating a private key')
my_key = rand_coprime(P-1)

LOG.info('encrypting and shuffling my downs/ups')
M_my_downs = [modpow(x, my_key) for x in my_downs]
M_my_ups = [modpow(x, my_key) for x in my_ups]
random.shuffle(M_my_downs)
random.shuffle(M_my_ups)

# listen or connect to host:port
c = interact(sys.argv[2])

LOG.info('sending my downs/ups encrypted with my key...')
c.sendall(pickle.dumps([M_my_downs, M_my_ups]))
H_his_downs, H_his_ups = pickle.loads(c.recv(2*SECURITY*NBITS//8*3))
LOG.info('...received his downs/ups encrypted with his key')

LOG.info('bi-encrypting (with my key) and shuffling his downs/ups')
HM_his_downs = [modpow(x, my_key) for x in H_his_downs]
HM_his_ups = [modpow(x, my_key) for x in H_his_ups]
random.shuffle(HM_his_downs)
random.shuffle(HM_his_ups)

LOG.info('sending his bi-encrypted downs/ups...')
c.sendall(pickle.dumps([HM_his_downs, HM_his_ups]))
HM_my_downs, HM_my_ups = pickle.loads(c.recv(2*SECURITY*NBITS//8*3))
LOG.info('...received my bi-encrypted downs/ups')

LOG.info('n. insections of my_downs and his_ups: %d (is my_value > his_value?)',
         len(set(HM_my_downs) & set(HM_his_ups)))
LOG.info('n. insections of my_ups and his_downs: %d (is his_value > my_value?)',
         len(set(HM_my_ups) & set(HM_his_downs)))
