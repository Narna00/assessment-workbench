"""Escape a literal UTF-8 assertion value for an LDAP filter (RFC 4515)."""
import argparse


def escape(value):
    mapping={'\x00':r'\00','(':r'\28',')':r'\29','*':r'\2a','\\':r'\5c'}
    return ''.join(mapping.get(char,char) for char in value)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('literal')
    args=parser.parse_args()
    print(escape(args.literal))
