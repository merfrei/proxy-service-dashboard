"""
Run debug server
"""

import sys
import argparse


parser = argparse.ArgumentParser(description='PSDash - CLI server debug')
parser.add_argument('--dbcreate', type=bool, dest='dbc', default=False, help='Create the DB schema')
parser.add_argument('--run', type=bool, dest='run', default=False, help='Run the debug server')


if __name__ == '__main__':
    args = parser.parse_args()

    if not(args.dbc or args.run):
        print('Nothing to do')
        sys.exit(0)

    from app import db
    from app import psdash
    from app.views import register_blueprints

    if args.dbc:
        db.create_all()

    if args.run:
        register_blueprints(psdash)
        psdash.run(debug=True)
