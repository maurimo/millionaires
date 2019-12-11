# Millionaires
Yao's millionaires problem, simple python solution (inspired to Lin-Tzeng one) implemented for self learning

This program implements Lin-Tzeng simple solution to the millionaires problem, with a simple different
variant on the private set intersection. Use at your risk, this program was written for self learning
by a non-professional.

# Requirements
You must install sympy, actually this is only necessary for the gcd computation

# Usage
You can have one party run `python3 millionaires.py secret_num1 port` to listen on `port1` on her host, while the
other party can connect running `python3 millionaires.py secret_num2 host:port` to connect.

# Algorithm
Lin-Tzeng method says that from my and otyher party's secrets we can compute additional numbers (my `ups` and
his `downs`) that are number bigger than my secret, and smaller than other party's secrets. My secret will be
smaller if and only if one of my `ups` equals exactly one of his `downs`. 

For the private intersection (where we only want to know if there is a non-empty intersection, and nobody
should know WHICH elements intersect, as it would disclose information about the other party's secret) I used
the following simple algorithm, inspired to the Diffie-Hellman key exchange:

My set is encrypted with my key (`x` -> `x^e`, for all `x` in my set) and sent to the other party (scrambled),
the other party does the same (`y` -> `y^f`, for all `y` in his set). The other party's `y^f` are encrypted
with my key `y^ef` and sent back (scrambled), while we also retrieve `x^ef`. Every party can now compare the
scrambled sets and check if they have non-empty intersection.