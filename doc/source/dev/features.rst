An Overview of Features
=======================

The Cement CLI Application Framework provides the following features for
every application (out of the box):

 * Multiple Configuration file parsing (default: /etc, ~/)
 * Command line argument and option parsing
 * Dual Console/File Logging Support
 * Internal and External (3rd Party) Plugin support
 * Basic "hook" support
 * MVC support for advanced application design
 * Text output rendering with Genshi templates
 * Json output rendering - The Cement CLI-API
    

Config File Parsing
-------------------

Config file parsing is provided by the standard ConfigObj.  The configuration 
object is stored in the root namespaces config member and can be accessed as:

.. code-block:: python

    from cement.core.namespace import get_config
    config = get_config()


The global config dictionary is generated [and overridden] in the following 
order:

 * defaults (set in ./yourapp/core/config.py)
 * /etc/yourapp/yourapp.conf
 * %(prefix)/etc/yourapp.conf
 * ~/.yourapp.conf
 

In the above, '%(prefix)' is a hard coded setting which points to 
'~/.yourapp/' by default (sane for development/no config situation).  Some
applications need a set location that all files belong in such as 
/var/lib/yourapp in which case the hard coded prefix can be changed.


Command Line Argument and Option Parsing
----------------------------------------

Command line arguments and options are parsed via OptParse for each namespace.
The base application owns the 'root' namespace, where as additional namespaces
branch off of that as illustrated below.  

.. code-block:: text

    # options and commands for root namespace
    $ helloworld --help 
    
    # options and subcommands for 'example' namespace
    $ helloworld example --help 
    

Namespaces have an option to 'merge_root_options' where their OptParse object
will merge in all of the options from the root namespace.  For example, the
options --debug, --quiet, --json are all root namespace options that are
merged into the 'example' namespace by default.

Options parsed from the command line will overwrite config options if the 
name of the option matches the config option.  For example, when passing the 
'--debug' option at command line, the root_config['debug'] setting is set to
True.


Logging
-------

Logging is provided by the standard 'logging' facility. By default Cement 
configures both a console log, as well as a file log.  This is fully 
configurable however in your applications configuration.  If no log_file is 
specified, none will be created.  If 'log_to_console' is false, nothing will 
be logged to console.  

The log level is determined by 'log_level' in your configuration, and is one
of the following:

    * info
    * warn
    * error
    * fatal
    * debug
 
Note that there are built in command line options that over ride these as well.
The --quiet option forces no console output at all (including print 
statements) and the --debug option forces console output, and full logging
at every level.  Debug should only be enabled for troubleshooting.

The logger can be accessed anywhere in your application by the following:

.. code-block:: python

    from cement.core.log import get_logger
    
    log = get_logger(__name__)
    log.info("This is an info message")
    log.error("This is an error message")
    log.debug("KAPLA!")


Plugin Support
--------------

Cement provides support for both internal and external (third party) plugins.
Internal plugins are those build as part of your base application, meaning
they will ship with your application and exist under ./yourapp/ source tree.
External plugins exist outside of your application and allow third parties to
build plugins that tie into your application.

External applications can be generated for your application via the paster 
utility:

.. code-block:: text

    $ paster cement-plugin yourapp myplugin
    
    $ cd yourapp-plugin-myplugin
    
    $ python setup.py develop


Plugins provide additional controllers, models, helpers, and templates to 
your application and function as if they were built into it directly.  The
plugin system is also designed to allow and encourage portability.  A plugin
can be imported into any other application built on cement.  Additionally,
The Rosendale Project was created to specifically build shared plugins for
applications built on Cement.


Hook Support
------------

Cement provides hook support for both the Cement framework, as well as your
applications and plugins.  Hooks are easily defined, registered, and run:

.. code-block:: python

    from cement.core.hook import define_hook, register_hook, run_hooks
    
    define_hook('myhook_hook')
    
    @register_hook(weight=10)
    def myhook_hook(*args, **kwargs):
        # do something
        return True
    
    @register_hook(weight=-99)
    def myhook_hook(*args, **kwargs):
        # do something else, but do it first, because I need to run before
        # everyone else...  my weight is -99.
        return True

    for res in run_hooks('myhook_hook'):
        # do something with res
        pass


This is a simple example, but the idea is... hooks can be defined either in 
your application, or in plugins.  You can then register a function into that 
hook meaning when the hook is called, that function will be executed in the 
order of 'weight'.  Finally, to run all functions that have been defined for 
that hook, we use the run_hooks() method.  

*Note: run_hooks() yields its results, therefore you must iterate over it.*
    

Model, View, Controller Design
------------------------------

Cement encourages good programmatic design and habits by organizing your 
application into separate model, view, controller pieces. 

    model
        The model can be any arbitrary object class, or can be something like 
        an SQLAlchemy declarative base.

    view
        The view is generated by the Genshi Text Template engine, allowing
        you to keep your controller clean and free of unnecessary print
        statements.
        
    controller
        The controller provides an outlet to expose commands to the 
        application.


Json Output Rendering - The Cement CLI-API
------------------------------------------

Now, sit back down and let me explain before you ask "Why in the world would 
you output Json from a command line application?".  It might not make sense
at first, but it does to me.  As a Linux Engineer bringing a number of 
utilities together to generate the output you want is always a fun task.  Be
it using sed, awk, grep, etc...  we're always having to mangle STDOUT and 
format it for our needs at that time.  

That said, parsing output is not only unpredictable, it doesn't scale.  Now
imagine a world where every command line application [optionally] spit out 
Json?  There is so much more you can do with a standard format such as Json,
Than parsing random output which differs from application to application.

All reasoning aside, Cement builds in an optional engine that renders command 
output as Json to the console.  This is triggered by the '--json' command
line option, and is what we like to call the Cement CLI-API.  Regardless of
the language, be it PERL, Ruby, Etc...  if they can speak Json then they can
access your application directly via a system call and get back data that they
can use without having to tie into your python libraries.


