# Copyright 2009-2010 Ram Rachum.
# This program is distributed under the LGPL2.1 license.


import copy
import Queue
import sys
import os
import threading
import time

from garlicsim.general_misc import import_tools
from garlicsim.general_misc import sys_tools
from garlicsim.general_misc import string_tools
from garlicsim.general_misc import cute_profile
from garlicsim.general_misc.reasoned_bool import ReasonedBool

import garlicsim
from garlicsim.asynchronous_crunching import \
     BaseCruncher, CrunchingProfile, ObsoleteCruncherException


__all__ = ['PiCloudCruncher']    

# blocktodo: remove `_profile=True` everywhere.

#@cute_profile.profile_ready(condition=lambda *args, **kwargs: True, off_after=False)
def step_and_go(state, step_iterator_getter, step_profile, clock_target,
                time_to_run):
    import cloud
    if state.clock >= clock_target or time_to_run < 0.01:
        return ([], None)
    
    my_time_to_run = min(1.2, time_to_run)
    time_to_stop = time.time() + my_time_to_run
    step_iterator = step_iterator_getter(state, step_profile)
    current_state = state
    new_states = []
    while (current_state.clock < clock_target) and \
          (time.time() < time_to_stop):
        current_state = step_iterator.next()
        new_states.append(current_state)

    print('Produced states with clocks: %s.' % \
          [state.clock for state in new_states])
        
    if current_state.clock < clock_target:
        new_jid = cloud.call(step_and_go, state, step_iterator_getter,
                             step_profile, clock_target,
                             time_to_run - my_time_to_run, _high_cpu=True)
    else:
        new_jid = None
        
    return (
        new_states,
        new_jid
    )


class PiCloudCruncher(BaseCruncher, threading.Thread):
    
    gui_explanation = string_tools.docstring_trim(
    '''
    PiCloudCruncher:
    
     - Works by using the `cloud` module supplied by PiCloud, Inc.
     
     - Offloads the crunching into the cloud, relieving this computer of the\
       CPU stress.
     
     - Requires a working internet connection and a PiCloud account. Visit
       http://picloud.com to get one.
     '''
    )
    
    def __init__(self, crunching_manager, initial_state, crunching_profile):
        BaseCruncher.__init__(self, crunching_manager,
                              initial_state, crunching_profile)
        threading.Thread.__init__(self)
        
        cloud = import_tools.import_if_exists('cloud', silent_fail=True)
        if not cloud:
            raise ImportError("The `cloud` module is needed. Get it at "
                              "http://picloud.com.")

        if self.project.simpack_grokker.history_dependent:
            raise garlicsim.misc.GarlicSimException(
                "PiCloudCruncher can't handle history-dependent simulations."
            )
        
        
        self.step_iterator_getter = \
            self.project.simpack_grokker.get_step_iterator
        self.history_dependent = self.project.simpack_grokker.history_dependent

        self.last_clock = initial_state.clock

        self.daemon = True

        self.work_queue = Queue.Queue()
        ''' 
        Queue for putting completed work to be picked up by the main thread.

        In this queue the cruncher will put the states that it produces, in
        chronological order. If the cruncher is being given a new crunching
        profile which has a new and different step profile, the cruncher
        will put the new step profile in this queue in order to signal that
        from that point on, all states were crunched with that step profile.
        '''

        self.order_queue = Queue.Queue()
        '''Queue for receiving instructions from the main thread.'''


    start = threading.Thread.start
    
        
    def run(self):
        '''
        Internal method.

        This is called when the cruncher is started. It just calls the
        main_loop method in a try clause, excepting ObsoleteCruncherException;
        That exception means that the cruncher has been retired in the middle
        of its job, so it is propagated up to this level, where it causes the
        cruncher to terminate.
        '''
        try:
            self.main_loop()
        except ObsoleteCruncherException:
            return


    def main_loop(self):
        '''
        The main loop of the cruncher.

        Crunches the simulations repeatedly until the crunching profile is
        satisfied or a 'retire' order is received.
        '''

        import cloud
        
        self.step_profile = self.crunching_profile.step_profile

        state = self.initial_state

        order = None

        try:
            while True:
                clock_target = self.crunching_profile.clock_target
                current_clock = state.clock
                time_to_run = 5
                initial_jid = cloud.call(step_and_go,
                                         state,
                                         self.step_iterator_getter,
                                         self.step_profile,
                                         clock_target,
                                         time_to_run,
                                         _high_cpu=True,
                                         )#_profile=True)
                jid = initial_jid
                while True:
                    (states, jid) = cloud.result(jid)
                    for state in states:
                        self.work_queue.put(state)
                    if not jid:
                        break
                    
                self.check_crunching_profile(state)
                order = self.get_order()
                if order:
                    self.process_order(order)
        except garlicsim.misc.WorldEnded:
            self.work_queue.put(
                garlicsim.asynchronous_crunching.misc.EndMarker()
            )

    

    def check_crunching_profile(self, state):
        '''
        Check if the cruncher crunched enough states. If so retire.

        The crunching manager specifies how much the cruncher should crunch.
        We consult with it to check if the cruncher has finished, and if it did
        we retire the cruncher.
        '''
        if self.crunching_profile.state_satisfies(state):
            raise ObsoleteCruncherException("We're done working, the clock "
                                            "target has been reached. "
                                            "Shutting down.")

    
    def get_order(self):
        '''
        Attempt to read an order from the order_queue, if one has been sent.

        Returns the order.
        '''
        try:
            return self.order_queue.get(block=False)
        except Queue.Empty:
            return None


    def process_order(self, order):
        '''Process an order receieved from order_queue.'''
        if order == 'retire':
            raise ObsoleteCruncherException("Cruncher received a 'retire' "
                                            "order; Shutting down.")

        elif isinstance(order, CrunchingProfile):
            self.process_crunching_profile_order(order)


    def process_crunching_profile_order(self, order):
        '''Process an order to update the crunching profile.'''
        if self.crunching_profile.step_profile != order.step_profile:
            raise ObsoleteCruncherException('Step profile changed; Shutting '
                                            'down. Crunching manager should '
                                            'create a new cruncher.')
        self.crunching_profile = order


    def retire(self):
        '''
        Retire the cruncher. Thread-safe.

        Causes it to shut down as soon as it receives the order.
        '''
        self.order_queue.put('retire')        


    def update_crunching_profile(self, profile):
        '''Update the cruncher's crunching profile. Thread-safe.'''
        self.order_queue.put(profile)


    def is_alive(self):
        return threading.Thread.isAlive(self)
    
    
    @staticmethod
    def can_be_used_with_simpack_grokker(simpack_grokker):
        '''
        Return whether `ProcessCruncher` can be used with `simpack_grokker`. 
        blocktododoc
        
        For `ProcessCruncher` to be usable, the `multiprocessing` module must
        be installed. Assuming it's installed, `ProcessCruncher` can be used if
        and only if the simpack is not history-dependent.
        '''
        
        if simpack_grokker.history_dependent:
            return ReasonedBool(
                False,
                "`PiCloudCruncher` does not support history-dependent "
                "simulations yet."
            )
        
        elif sys_tools.is_pypy:
            return ReasonedBool(
                False,
                "`PiCloudCruncher` can't be used on PyPy, which you are "
                "currently running on. It can only be  used on CPython."
            )
        
        elif not import_tools.exists('cloud'):
            return ReasonedBool(
                False,
                "`PiCloudCruncher` can't be used until you install the "
                "`cloud` module from http://pypi.python.org/pypi/cloud"
            )
        
        else:
            return True


