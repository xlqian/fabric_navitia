#import all env for fabric to find them
from fabfile.env.platforms import *
from fabfile.tasks import *

from fabfile.custom_tasks import *
from fabfile.prod_tasks import *

# If we want to narrow the list of public task, we can do it with the __all__
#__all__ = ['upgrade_all', 'env']
