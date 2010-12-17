# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `CrunchingProfile` class.

See its documentation for more information.
'''

import garlicsim.misc


__all__ = ['CrunchingProfile']


class CrunchingProfile(object):
    '''Instructions that a cruncher follows when crunching the simulation.'''
    
    def __init__(self, clock_target, step_profile):
        '''
        Construct the CrunchingProfile.
        
        `clock_target` is the clock until which we want to crunch.
        `step_profile` is the step profile we want to use.
        '''
        
        self.clock_target = clock_target
        '''We crunch until we get a clock of `.clock_target` or higher.'''

        assert isinstance(step_profile, garlicsim.misc.StepProfile)
        self.step_profile = step_profile
        '''The step profile we want to be used with the step function.'''
  
    def state_satisfies(self, state):
        '''
        Check whether a state has a clock high enough to satisfy this profile.
        '''
        return state.clock >= self.clock_target
    
    def raise_clock_target(self, clock_target):
        '''Make `.clock_target` at least as big as the given `clock_target`.'''
        if self.clock_target < clock_target:
            self.clock_target = clock_target
    
    def __eq__(self, other):
        return isinstance(other, CrunchingProfile) and \
               self.clock_target == other.clock_target and \
               self.step_profile == other.step_profile

    def __hash__(self):
        # Defining __hash__ because there's __eq__ which makes the default
        # __hash__ disappear on Python 3.
        return id(self)

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        '''
        Get a string representation of the crunching profile.
        
        Example output:
        
            CrunchingProfile(clock_target=Infinity,
            step_profile=StepProfile(<unbound method State.step>))
        '''
        stuff = []
        stuff.append('clock_target=%s' % self.clock_target)
        stuff.append('step_profile=%s' % self.step_profile.__repr__(short_form=True))
        temp = ", ".join(stuff)
        return ('CrunchingProfile(%s)' % temp)
    
    
    