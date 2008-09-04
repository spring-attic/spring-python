"""
   Copyright 2006-2008 SpringSource (http://springsource.com), All Rights Reserved

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

import cherrypy
import logging
import os
import noxml
from cherrypy._cpwsgi import wsgiApp
from cherrypy._cpwsgiserver import CherryPyWSGIServer
from cherrypy._cpserver import Server
from springpython.security.context import SecurityContextHolder

class WSGIServerWithMiddleware(object):
    def __init__(self, middleware):
        self.middleware = middleware
    def __call__(self):
        return CherryPyWSGIServer(("", 8001), self.middleware[0])

class MiddlewareServer(Server):
    def start(self, middleware):
        Server.start(self, initOnly=False, serverClass=WSGIServerWithMiddleware(middleware))
        
if __name__ == '__main__':
    """This allows the script to be run as a tiny webserver, allowing quick testing and development.
    For more scalable performance, integration with Apache web server would be a good choice."""

    # This turns on debugging, so you can see everything Spring Python is doing in the background
    # while executing the sample application.

    logger = logging.getLogger("springpython")
    loggingLevel = logging.DEBUG
    logger.setLevel(loggingLevel)
    ch = logging.StreamHandler()
    ch.setLevel(loggingLevel)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s") 
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # This sample is just like petclinic-xml.py, only the wiring and order of dependency is resolved through decorators
    # and function calls. All the core pieces work just the same and are reusable, giving
    # you the flexibility and freedom to code it as you want.

    applicationContext = noxml.PetClinicClientAndServer()
    
    # Everything below is identical between petclinic.py and petclinic-noxml.py
    
    SecurityContextHolder.setStrategy(SecurityContextHolder.MODE_THREADLOCAL)

    # CherryPy always starts with cherrypy.root when trying to map request URIs
    # to objects. In this case, it is being assigned an object that was created in the
    # IoC container, allowing the web server components to be totally decoupled from the
    # view component.
    cherrypy.root = applicationContext.getComponent(componentId = "root")
    cherrypy.root.login = applicationContext.getComponent(componentId = "loginForm")

    cherrypy.server = MiddlewareServer()

    # Configure cherrypy programmatically.
    cherrypy.config.update({
                            "global": {
                                       "server.socket_port": 8001
                            },
                            "/": {
                                  "static_filter.root": os.getcwd()
                            },
                            "/images": {
                                "static_filter.on": True,
                                "static_filter.dir": "images"
                            },
                            "/html": {
                                "static_filter.on": True,
                                "static_filter.dir": "html"
                            },
                            "/styles": {
                                "static_filter.on": True,
                                "static_filter.dir": "css"
                            },
                            "/scripts": {
                                "static_filter.on": True,
                                "static_filter.dir": "js"
                            },
                            "/login/images": {
                                "static_filter.on": True,
                                "static_filter.dir": "images"
                            }
                        })

    middleware = applicationContext.getComponent(componentId = "filterChainProxy")
    middleware.application = wsgiApp
    
    # Start the CherryPy server.
    cherrypy.server.start(middleware=[middleware])
