import logging
import time

from qe.exceptions import Method_Not_Allowed_Exception
from qe.utils import to_str, wait_until
import base


log = logging.getLogger(__name__)


class UnifiedJob(base.Base):
    '''
    Base class for unified job pages (e.g. project_updates, inventory_updates
    and jobs).
    '''

    def __str__(self):
        # NOTE: I use .replace('%', '%%') to workaround an odd string
        # formatting issue where result_stdout contained '%s'.  This later caused
        # a python traceback when attempting to display output from this method.
        items = ['id', 'name', 'status', 'failed', 'result_stdout', 'result_traceback',
                 'job_explanation', 'job_args']
        info = []
        for item in filter(lambda x: hasattr(self, x), items):
            info.append('{0}:{1}'.format(item, to_str(getattr(self, item))))
        output = '<{0.__class__.__name__} {1}>'.format(self, ', '.join(info))
        return output.replace('%', '%%')

    @property
    def is_completed(self):
        '''
        Return whether the current task has finished.  This does not indicate
        whether the task completed successfully.
        '''
        return self.status.lower() in ['successful', 'failed', 'error', 'canceled']

    @property
    def is_successful(self):
        '''
        Return whether the current has completed successfully.  This means that:
         * self.status == 'successful'
         * self.has_traceback == False
         * self.failed == False
        '''
        return 'successful' == self.status.lower() and \
            not (self.has_traceback or self.failed)

    @property
    def has_traceback(self):
        '''
        Return whether a traceback has been detected in result_traceback or
        result_stdout
        '''
        return 'Traceback' in self.result_traceback or \
               'Traceback' in self.result_stdout

    def wait_until_status(self, status, interval=1, verbose=0, timeout=60, **kw):
        if not isinstance(status, (list, tuple)):
            '''coerce 'status' parameter to a list'''
            status = [status]
        return wait_until(self, 'status', status, interval=interval, verbose=verbose, timeout=timeout,
                          start_time=time.strptime(self.created, '%Y-%m-%dT%H:%M:%S.%fZ'), **kw)

    def wait_until_started(self, interval=1, verbose=0, timeout=60):
        return self.wait_until_status(
            ('pending', 'running', 'successful', 'failed', 'error', 'canceled',),
            interval=interval, verbose=verbose, timeout=timeout)

    def wait_until_completed(self, interval=5, verbose=0, timeout=60 * 3, **kw):
        return self.wait_until_status(
            ('successful', 'failed', 'error', 'canceled',),
            interval=interval, verbose=verbose, timeout=timeout, **kw)

    def cancel(self):
        cancel = self.get_related('cancel')
        if not cancel.can_cancel:
            return
        try:
            cancel.post()
        except Method_Not_Allowed_Exception as e:
            # Race condition where job finishes between can_cancel
            # check and post.
            if "not allowed" not in e.message.get('error', ''):
                raise(e)

# backwards compatibility
Unified_Job_Page = UnifiedJob
