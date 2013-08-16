#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  debug.py
#  SphinxDoc.tmbundle
#  
#  Created by André Berg on 19.08.2012.
#  Copyright 2012 Berg Media. All rights reserved.
# 
#  Description: 
#  Contains facilities for debugging.
#
# pylint: disable-msg=E1101
#

import sys
import linecache
from abc import ABCMeta, abstractmethod


class BasicTracer(object):
    '''Asbtract base class for a Tracer object.'''
    
    __metaclass__ = ABCMeta
            
    def __init__(self, module_globals):
        super(BasicTracer, self).__init__()
        self.module_globals = module_globals
        self.enabler_key = self.get_enabler_key()
    
    def get_enabler_key(self):
        return "__debug_enable_{0}".format(type(self).__name__.lower())
        
    @abstractmethod
    def trace(self, frame, event, arg, *args, **kwargs):
        '''Intended for subclasses to implement subclass-specific tracing logic.
        
        Whatever it returns will be passed as a parameter to C{sys.settrace()}.
        Therefore it must return C{self.trace} as required by C{settrace()}.
        @note: this method is abstract. It is not intended to be called 
               directly on C{BasicTracer}.
        @raise: C{RuntimeError} if called directly on C{BasicTracer}.
        '''
        raise RuntimeError('BasicTracer.trace() is abstract.')
    
    def enable(self):
        sys.settrace(self.trace)
        self.module_globals[self.enabler_key] = True
    
    def disable(self):
        self.module_globals[self.enabler_key] = False
        sys.settrace(None)

class LineTracer(BasicTracer):
    '''Line tracer. Traces each line as it is executed.'''
    
    def __init__(self, module_globals):
        super(LineTracer, self).__init__(module_globals)
        
    def trace(self, frame, event, arg):
        '''Trace lines as they are processed by the interpreter.'''
        if self.module_globals.get(self.enabler_key, False):
            if event == "line":
                lineno = frame.f_lineno
                filename = frame.f_globals["__file__"]
                if (filename.endswith(".pyc") or
                    filename.endswith(".pyo")):
                    filename = filename[:-1]
                name = frame.f_globals["__name__"]
                line = linecache.getline(filename, lineno)
                print "%s:%s: %s" % (name, lineno, line.rstrip())
            return self.trace
        else:
            return None

class FuncTracer(BasicTracer):
    '''Function tracer. Traces each function as it is executed.'''
    
    def __init__(self, module_globals):
        super(FuncTracer, self).__init__(module_globals)
        
    def trace(self, frame, event, arg, indent=[0]):
        if self.module_globals.get(self.enabler_key, False):
            if event == "call":
                indent[0] += 2
                print "-" * indent[0] + "> call function", frame.f_code.co_name
            elif event == "return":
                print "<" + "-" * indent[0], "exit function", frame.f_code.co_name
                indent[0] -= 2
            return self.trace
        else:
            return None
    
class LocalFuncTracer(BasicTracer):
    '''Local function tracer. Traces module local functions only. 
    
    Module local means functions which are defined in the module 
    owning the LocalFuncTracer instance on which enable() was called.
    '''
    
    def __init__(self, module_globals):
        super(LocalFuncTracer, self).__init__(module_globals)
    
    def trace(self, frame, event, arg, indent=[0]):
        if self.module_globals.get(self.enabler_key, False):
            if frame.f_globals["__file__"] == self.module_globals['__file__']:
                if event == 'call':
                    indent[0] += 2
                    print "-" * indent[0] + "> call function", frame.f_code.co_name
                elif event == "return":
                    print "<" + "-" * indent[0], "exit function", frame.f_code.co_name
                    indent[0] -= 2
            return self.trace
        else:
            return None
    
class FuncTracerFilter(object):
    '''Filter objects used by L{FilteredFuncTracer}.
    
    Currently supports filters for module paths,
    function names and events. A filter is simply
    a list of strings. Note that the meaning of 
    'to filter' changes depending on the filter
    being used: 
    
    - Module paths are filtered inclusive,
      meaning only functions found in modules with 
      a module path that matches an entry found
      in the list given by self.modules are being
      traced.
    
    - Functions names and events are filtered
      exclusive, meaning only functions *NOT*
      found in the list given by self.names and
      self.events respectively are being traced.
    
    Using a FuncTracerFilter is simple:
    
        >>> tracer = FilteredFuncTracer(globals())
        >>> filter = FuncTracerFilter(tracer)
        >>> tracer.set_filter(filter)
    
    Note that this will instantiate C{FuncTracerFilter}
    with the following defaults:
    
    self.modules = tracer.module_globals['__file__']
    self.names = ['<genexpr>']
    self.events = []
    
    e.g. by default C{FuncTracerFilter} will make 
    the tracer only trace functions which are defined
    in the tracer's module, that don't have a name
    of '<genexpr>' and it will make it so that the 
    tracer traces all events (currently, 'call' and
    'return').

    If you want to customize some aspect, for example,
    let's assume you want to also exclude functions 
    named 'foo':
    
        >>> tracer = FilteredFuncTracer(globals())
        >>> filter = FuncTracerFilter(tracer)
        >>> filter.customize(names=filter.names.append('foo'))
        >>> tracer.set_filter(filter)
    '''
    def __init__(self, tracer):
        super(FuncTracerFilter, self).__init__()
        if not isinstance(tracer, BasicTracer):
            raise TypeError("Wrong type for argument 'tracer'. Got '%s' but should be instance of 'BasicTracer'" % type(tracer).__name__)
        self.tracer = tracer
        self.modules = [self.tracer.module_globals['__file__']]
        self.names = ['<genexpr>']
        self.events = []
    
    def customize(self, modules=None, names=None, events=None, mode='append'):
        """Override defaults after the filter has been created.
        
        @param modules: customize module paths.
        @type modules: C{list<string>}
        @param names: customize function names.
        @type names: C{list<string>}
        @param events: customize events.
        @type events: C{list<string>}
        @param mode: append to defaults or override.
                     the default is to append.
        @type mode: C{string}
        @raise: C{ValueError} if C{mode} is not one of
                C{['override', 'append']}.
        """ 
        allowed_modes = ['override', 'append']
        if mode not in allowed_modes:
            raise ValueError("value for parameter 'mode' must be one of %r" % (allowed_modes))
        if mode == 'override':
            if modules:
                self.modules = modules
            if names:
                self.names = names
            if events:
                self.events = events
        else: # mode == 'append'
            if modules:
                self.modules.append(modules)
            if names:
                self.names.append(names)
            if events:
                self.events.append(events)
            
        
        
class FilteredFuncTracer(BasicTracer):
    '''Function tracer. Traces each function as it is executed.
    
    Additionally supports selective output by means of a filter.
    See L{FuncTracerFilter} for details.
    '''
    
    def __init__(self, module_globals):
        super(FilteredFuncTracer, self).__init__(module_globals)
        
    def set_filter(self, afilter=None):
        """Set filter to use. For details see L{FuncTracerFilter}.
        @param afilter: the filter to use. If C{None} sets up
                        its own instance of a default filter.
        @type afilter: C{FuncTracerFilter}
        """
        if afilter is None:
            self.afilter = FuncTracerFilter(self)
        elif isinstance(afilter, FuncTracerFilter):
            self.afilter = afilter
        else:
            raise TypeError("Wrong type for argument 'afilter'. Got '%s' but should be 'FuncTracerFilter'" % type(afilter).__name__)

    def trace(self, frame, event, arg, indent=[0]):
        if self.module_globals.get(self.enabler_key, False):
            if frame.f_globals["__file__"] in self.afilter.modules and frame.f_code.co_name not in self.afilter.names:
                if event == 'call':
                    indent[0] += 2
                    if not event in self.afilter.events:
                        print "-" * indent[0] + "> call function", frame.f_code.co_name
                elif event == "return":
                    if not event in self.afilter.events:
                        print "<" + "-" * indent[0], "exit function", frame.f_code.co_name
                    indent[0] -= 2
            return self.trace
        else:
            return None

        
if __name__ == '__main__':
    
    def dummy(*args, **kwargs):
        print("dummy called with args = %r, kwargs = %r" % (args, kwargs))
        
    ltracer = LineTracer(globals())
    ltracer.enable()
    print("test")
    print(ltracer.get_enabler_key())
    ltracer.disable()
    
    ftracer = FuncTracer(globals())
    ftracer.enable()
    print("test")
    print(ftracer.get_enabler_key())
    ftracer.disable()
    
    lftracer = LocalFuncTracer(globals())
    lftracer.enable()
    print("test")
    print(lftracer.get_enabler_key())
    dummy(1,2,3, foo='bar')
    lftracer.disable()
    
    fftracer = FilteredFuncTracer(globals())
    filter = FuncTracerFilter(fftracer)
    filter.customize(names=['get_enabler_key'], events=['return'])
    fftracer.set_filter(filter)
    fftracer.enable()
    print("test")
    print(fftracer.get_enabler_key())
    dummy(1,2,3, foo='bar')
    fftracer.disable()
