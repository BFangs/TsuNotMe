import logging
from time import time
from experiment import all_points, db, connect_to_db

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def seed_time(source):
    """time it takes to seed database"""

    ts = time()
    all_points(source)
    print 'Seeding {}s Took {}s'.format(source, (time() - ts))


def query_time():
    """time it takes to finish query"""

    ts = time()

    print 'Took {}s'.format(time() - ts)

if __name__ == '__main__':
    from server import app
    connect_to_db(app, db_url='postgresql:///allpoints')
    print "connected to db"
    db.create_all()
    print "tables created"
