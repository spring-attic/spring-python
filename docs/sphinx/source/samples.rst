Samples
=======

PetClinic
---------

PetClinic is a sample application demonstrating the usage of Spring Python.

* It uses `CherryPy <https://cherrypy.org/>`_ as the web server object.

* A `detailed design document <https://fisheye.springsource.org/browse/se-springpython-py/samples/petclinic/cherrypy/html/petclinic.html>`_
  (NOTE: find latest version, and click on raw) is
  part of the source code. You can read it from here or by clicking on a
  hyperlink while running the application.

How to run
++++++++++

.. highlight:: bash

Assuming you just checked out a copy of the source code, here are the steps to
run PetClinic::

  bash$ cd /path/you/checked/out/springpython
  bash$ cd samples/petclinic
  bash$ python configure.py

At this point, you will be prompted for MySQL's root password. This is NOT
your system's root password. This assumes you have a MySQL server running.
After that, it will have setup database *petclinic*::

  bash$ cd cherrypy
  bash$ python petclinic.py

This assumes you have `CherryPy 3 <https://cherrypy.org/>`_  installed. It probably
*won't* work if you are still using CherryPy 2. NOTE: If you are using Python 2.5.2+, you must install
CherryPy 3.1.2+. The older version of CherryPy (3.1.0) only works pre-2.5.2.

Finally, after launching it, you should see a nice URL at the bottom:
http://localhost:8080. Well, go ahead! Things should look good now!

.. image:: gfx/PetClinic-snapshot.png
    :align: center

Spring Wiki
-----------

Spring Wiki is a wiki engine based that uses mediawiki's markup language.
It utilizes the same stylesheets to have a very wikipedia-like feel to it.

TODO: Add persistence. Currently, Spring Wiki only stores content in current
memory. Shutting it down will cause all changes to be lost.

Spring Bot
----------

This article will show how to write an IRC bot to manage a channel for your open
source project.

Why write a bot?
++++++++++++++++

I read an article,
`Building a community around your open source project <https://magazine.redhat.com/2007/09/21/building-a-community-around-your-open-source-project/>`_,
that talked about setting up an IRC channel for your project. This is a route
to support existing users, and allow them to work with each other.

I became very interested in writing some IRC bot, and I since my project is
based on Python, well, you can probably guess what language I wanted to write
it in.

IRC Library
+++++++++++

To build a bot, it pays to have use an already written library. I discovered python-irclib.

.. highlight:: bash

For Ubuntu users::

  % sudo apt-get install python-irclib

This bot also sports a web page using `CherryPy <https://cherrypy.org/>`_.
You also need to install that as well.

Articles
>>>>>>>>

Well, of course I started reading. The documentation from the project's web
site was minimal. Thankfully, I found some introductory articles that work
with python-irclib.

* http://www.devshed.com/c/a/Python/IRC-on-a-Higher-Level/
* http://www.devshed.com/c/a/Python/IRC-on-a-Higher-Level-Continued/
* http://www.devshed.com/c/a/Python/IRC-on-a-Higher-Level-Concluded/

What I built
++++++++++++

.. highlight:: python

Using this, I managed to get something primitive running. It took me a while
to catch on that posting private messages on a channel name instead of a user
is the way to publicly post to a channel. I guess it helped to trip through
the `IRC RFC <https://www.irchelp.org/irchelp/rfc/rfc.html>`_ manual, before catching on to this.

At this stage, you may wish to get familiar with `regular expressions in Python <https://www.amk.ca/python/howto/regex/>`_.
You will certainly need this in order to make intelligent looking patterns.
Anything more sophisticated would probably require `PLY <https://www.dabeaz.com/ply/>`_.

What I really like is that fact that I built this application in approximately
24 hours, counting the time to learn how to use python-irclib. I already knew
ow to build a Spring Python/CherryPy web application. The history pages on this
article should demonstrate how long it took.

NOTE: This whole script is contained in one file, and marked up as::

  """
     Copyright 2006-2008 SpringSource (https://springsource.com), All Rights Reserved

     Licensed under the Apache License, Version 2.0 (the "License");
     you may not use this file except in compliance with the License.
     You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

     Unless required by applicable law or agreed to in writing, software
     distributed under the License is distributed on an "AS IS" BASIS,
     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     See the License for the specific language governing permissions and
     limitations under the License.
  """


IRC Bot
>>>>>>>

So far, this handy little bot is able to monitor the channel, log all
communications, persistently fetch/store things, and grant me operator status
when I return to the channel. My next task is to turn it into a web app using
Spring Python. That should let me have a web page to go along with the channel::

    class DictionaryBot(ircbot.SingleServerIRCBot):
        def __init__(self, server_list, channel, ops, logfile, nickname, realname):
            ircbot.SingleServerIRCBot.__init__(self, server_list, nickname, realname)
            self.datastore = "%s.data" % self._nickname
            self.channel = channel
            self.definition = {}
            try:
                f = open(self.datastore, "r")
                self.definition = cPickle.load(f)
                f.close()
            except IOError:
                pass
            self.whatIsR = re.compile(",?\s*[Ww][Hh][Aa][Tt]\s*[Ii][Ss]\s+([\w ]+)[?]?")
            self.definitionR = re.compile(",?\s*([\w ]+)\s+[Ii][Ss]\s+(.+)")
            self.ops = ops
            self.logfile = logfile

        def on_welcome(self, connection, event):
            """This event is generated after you connect to an irc server, and should be your signal to join your target channel."""
            connection.join(self.channel)

        def on_join(self, connection, event):
            """This catches everyone who joins. In this case, my bot has a list of whom to grant op status to when they enter."""
            self._log_event(event)
            source = event.source().split("!")[0]
            if source in self.ops:
                connection.mode(self.channel, "+o %s" % source)

        def on_mode(self, connection, event):
            """No real action here, except to log locally every mode action that happens on my channel."""
            self._log_event(event)

        def on_pubmsg(self, connection, event):
            """This is the real meat. This event is generated everytime a message is posted to the channel."""
            self._log_event(event)

            # Capture who posted the messsage, and what the message was.
            source = event.source().split("!")[0]
            arguments = event.arguments()[0]

            # Some messages are meant to signal this bot to do something.
            if arguments.lower().startswith("!%s" % self._nickname):
                # "What is xyz" command
                match = self.whatIsR.search(arguments[len(self._nickname)+1:])
                if match:
                    self._lookup_definition(connection, match.groups()[0])
                    return

                # "xyz is blah blah" command
                match = self.definitionR.search(arguments[len(self._nickname)+1:])
                if match:
                    self._set_definition(connection, match.groups()[0], match.groups()[1])
                    return

            # There are also some shortcut commands, so you don't always have to address the bot.
            if arguments.startswith("!"):
                match = re.compile("!([\w ]+)").search(arguments)
                if match:
                    self._lookup_definition(connection, match.groups()[0])
                    return

        def getDefinitions(self):
            """This is to support a parallel web app fetching data from the bot."""
            return self.definition

        def _log_event(self, event):
            """Log an event to a flat file. This can support archiving to a web site for past activity."""
            f = open(self.logfile, "a")
            f.write("%s::%s::%s::%s\n" % (event.eventtype(), event.source(), event.target(), event.arguments()))
            f.close()

        def _lookup_definition(self, connection, keyword):
            """Function to fetch a definition from the bot's dictionary."""
            if keyword.lower() in self.definition:
                connection.privmsg(self.channel, "%s is %s" % self.definition[keyword.lower()])
            else:
                connection.privmsg(self.channel, "I have no idea what %s means. You can tell me by sending '!%s, %s is <your definition>'" % (keyword, self._nickname, keyword))

        def _set_definition(self, connection, keyword, definition):
            """Function to store a definition in cache and to disk in the bot's dictionary."""
            self.definition[keyword.lower()] = (keyword, definition)
            connection.privmsg(self.channel, "Got it! %s is %s" % self.definition[keyword.lower()])
            f = open(self.datastore, "w")
            cPickle.dump(self.definition, f)
            f.close()

I have trimmed out the instantiation of this bot class, because that part isn't
relevant. You can go and immediately reuse this bot to manage any channel you have.

Web App
>>>>>>>

Well, after getting an IRC bot working that quickly, I want a nice interface to
see what it is up to. For that, I will use Spring Python  and build a
Spring-based web app::

    def header():
        """Standard header used for all pages"""
        return """
            <!--

                Coily :: An IRC bot used to manage the #springpython irc channel (powered by CherryPy/Spring Python)

            -->

            <html>
            <head>
            <title>Coily :: An IRC bot used to manage the #springpython irc channel (powered by CherryPy/Spring Python)</title>
                <style type="text/css">
                        td { padding:3px; }
                        div#top {position:absolute; top: 0px; left: 0px; background-color: #E4EFF3; height: 50px; width:100%; padding:0px; border: none;margin: 0;}
                        div#image {position:absolute; top: 50px; right: 0%; background-image: url(images/spring_python_white.png); background-repeat: no-repeat; background-position: right; height: 100px; width:300px }
                </style>
            </head>

            <body>
                <div id="top">&nbsp;</div>
                <div id="image">&nbsp;</div>
                <br clear="all">
                <p>&nbsp;</p>
            """

    def footer():
        """Standard footer used for all pages."""
        return """
            <hr>
            <table style="width:100%"><tr>
                    <td><A href="/">Home</A></td>
                    <td style="text-align:right;color:silver">Coily :: a <a href="http://springpython.webfactional.com">Spring Python</a> IRC bot (powered by <A HREF="https://www.cherrypy.org">CherryPy</A>)</td>
            </tr></table>

            </body>
            """

    def markup(text):
        """Convert any https://xyz references into real web links."""
        httpR = re.compile(r"(http://[\w.:/?-]*\w)")
        alteredText = httpR.sub(r'<A HREF="\1">\1</A>', text)
        return alteredText

    class CoilyView:
        """Presentation layer of the web application."""

        def __init__(self, bot = None):
            """Inject a controller object in order to fetch live data."""
            self.bot = bot

        @cherrypy.expose
        def index(self):
            """CherryPy will call this method for the root URI ("/") and send
            its return value to the client."""

            return header() + """
                <H2>Welcome</H2>
                <P>
                Hi, I'm Coily! I'm a bot used to manage the IRC channel <a href="irc://irc.ubuntu.com/#springpython">#springpython</a>.
                <P>
                If you visit the channel, you may find I have a lot of information to offer while you are there. If I seem to be missing some useful definitions, then you can help grow my knowledge.
                <small>
                    <TABLE border="1">
                        <TH>Command</TH>
                        <TH>Description</TH>
                        <TR>
                            <TD>!coily, what is <i>xyz</i>?</TD>
                            <TD>This is how you ask me for a definition of something.</TD>
                        </TR>
                        <TR>
                            <TD>!<i>xyz</i></TD>
                            <TD>This is a shortcut way to ask the same question.</TD>
                        </TR>
                        <TR>
                            <TD>!coily, <i>xyz</i> is <i>some definition for xyz</i></TD>
                            <TD>This is how you feed me a definition.</TD>
                        </TR>
                    </TABLE>
                </small>
                <P>
                To save you from having to query me for every current definition I have, there is a link on this web site
                that lists all my current definitions. NOTE: These definitions can be set by other users.
                <P>
                <A href="listDefinitions">List current definitions</A>
                <P>
                """ + footer()

        @cherrypy.expose
        def listDefinitions(self):
            results = header()
            results += """
                    <small>
                    <TABLE border="1">
                        <TH>Keyword</TH>
                        <TH>Definition</TH>
                """
            for key, value in self.bot.getDefinitions().items():
                results += markup("""
                    <TR>
                        <TD>%s</TD>
                        <TD>%s</TD>
                    </TR>
                    """ % (value[0], value[1]))
            results += "</TABLE></small>"
            results += footer()
            return results


Putting it all together
>>>>>>>>>>>>>>>>>>>>>>>

Well, so far, I have two useful classes. However, they need to get launched
inside a script. This means objects need to be instantiated. To do this, I have
decided to make this a Spring app and use :doc:`Inversion of Control <objects>`.

So, I defined two contexts, one for the IRC bot and another for the web
application.

IRC Bot's application context
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

::

    class CoilyIRCServer(PythonConfig):
        """This container represents the context of the IRC bot. It needs to
        export information, so the web app can get it."""
        def __init__(self):
            super(CoilyIRCServer, self).__init__()

        @Object
        def remoteBot(self):
            return DictionaryBot([("irc.ubuntu.com", 6667)], "#springpython",
                ops=["Goldfisch"], nickname="coily",
                realname="Coily the Spring Python assistant", logfile="springpython.log")

        @Object
        def bot(self):
            exporter = PyroServiceExporter()
            exporter.service_name = "bot"
            exporter.service = self.remoteBot()
            return exporter


Web App's application context
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

::

    class CoilyWebClient(PythonConfig):
        """
        This container represents the context of the web application used to interact with the bot and present a
        nice frontend to the user community about the channel and the bot.\
        """
        def __init__(self):
            super(CoilyWebClient, self).__init__()

        @Object
        def root(self):
            return CoilyView(self.bot())

        @Object
        def bot(self):
            proxy = PyroProxyFactory()
            proxy.service_url = "PYROLOC://localhost:7766/bot"
            return proxy

Main runner
<<<<<<<<<<<

I fit all this into one executable. However, I quickly discovered that both
CherryPy web apps and irclib bots like to run in the main thread. This means
I need to launch two python shells, one running the web app, the other running
the ircbot, and I need the web app to be able to talk to the irc bot. This is
a piece of cake with Spring Python. All I need to utilize is a :doc:`remoting technology <remoting>`::

    if __name__ == "__main__":
        # Parse some launching options.
        parser = OptionParser(usage="usage: %prog [-h|--help] [options]")
        parser.add_option("-w", "--web", action="store_true", dest="web", default=False, help="Run the web server object.")
        parser.add_option("-i", "--irc", action="store_true", dest="irc", default=False, help="Run the IRC-bot object.")
        parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="Turn up logging level to DEBUG.")
        (options, args) = parser.parse_args()

        if options.web and options.irc:
            print "You cannot run both the web server and the IRC-bot at the same time."
            sys.exit(2)

        if not options.web and not options.irc:
            print "You must specify one of the objects to run."
            sys.exit(2)

        if options.debug:
            logger = logging.getLogger("springpython")
            loggingLevel = logging.DEBUG
            logger.setLevel(loggingLevel)
            ch = logging.StreamHandler()
            ch.setLevel(loggingLevel)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        if options.web:
            # This runs the web application context of the application. It allows a nice web-enabled view into
            # the channel and the bot that supports it.
            applicationContext = ApplicationContext(CoilyWebClient())

            # Configure cherrypy programmatically.
            conf = {"/":                {"tools.staticdir.root": os.getcwd()},
                    "/images":          {"tools.staticdir.on": True,
                                         "tools.staticdir.dir": "images"},
                    "/html":            {"tools.staticdir.on": True,
                                         "tools.staticdir.dir": "html"},
                    "/styles":          {"tools.staticdir.on": True,
                                         "tools.staticdir.dir": "css"}
                    }

            cherrypy.config.update({'server.socket_port': 9001})

            cherrypy.tree.mount(applicationContext.get_object(name = "root"), '/', config=conf)

            cherrypy.engine.start()
            cherrypy.engine.block()

        if options.irc:
            # This runs the IRC bot that connects to a channel and then responds to various events.
            applicationContext = ApplicationContext(CoilyIRCServer())
            coily = applicationContext.get_object("bot")
            coily.service.start()


Releasing your CherryPy web app to the internet
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Now that you have a CherryPy web app running, how about making it visible to
the internet?

.. highlight:: apache

If you already have an Apache web server running, and are using a Debian/Ubuntu
installation, you just need to create a file in */etc/apache2/sites-available* like
*coily.conf* with the following lines::

    RedirectMatch ^/coily$ /coily/

    ProxyPass /coily/ http://localhost:9001/
    ProxyPassReverse /coily/ http://localhost:9001/

    <LocationMatch /coily/.*>
        Order allow,deny
        Allow from all
    </LocationMatch>

.. highlight:: bash

Now need to softlink this into /etc/apache2/sites-enabled::

    % cd /etc/apache2/sites-enabled
    % sudo ln -s /etc/apache2/sites-available/coily.conf 001-coily

This requires that mod_proxy be enabled::

    % sudo a2enmod proxy proxy_http

Finally, restart Apache::

    % sudo /etc/init.d/apache2 --force-reload

It should be visible on the site now.

Come and visit Coily
>>>>>>>>>>>>>>>>>>>>

If you haven't figured it out yet, I use this code to run my own bot, Coily.
Unfortunately, at this time, I don't have a mechanism to make it run persistently.

External Links
++++++++++++++

`See this article reported in LinuxToday <https://www.linuxtoday.com/news_story.php3?ltsn=2007-10-12-009-26-OS-DV-NT>`_