Remote Hosted Demos
===================

These are demos that show off working with larger data and may be hard to run locally. That's actually a plus, you get to say that they work well "even over conference wifi".

* ocean demo downsampling

  4.4 GB ocean surface temp data data cube (HDF), progressive refinement, widgets

  http://162.243.42.178:9000/v5.0/bokeh/ocean/

* time series downsampling

  2.1 million points, linked panning, progressive refinement

  http://162.243.42.178:9000/v5.0/bokeh/timeseries/

* Taxis abstract rendering

  89 million rows, widgets, AR

  http://104.131.121.15:5006/bokeh/taxis/

  NOTE: This one is new/WIP. Currently a bit slow, also the URL may change, ping Hugo with any questions

Applet Demos
============

For now the best way I know to run these is to run separate Bokeh servers. To run these, cd to the example directory listed, run the bokeh-server command, and navigate to the given URL.

* examples/app/crossfilter (localhost:5010/bokeh/crossfilter/)

  bokeh-server --port=5010 --ws-port=5011  --zmqaddr="tcp://127.0.0.1:5610" --backend=memory --script=crossfilter_app.py

* examples/app/sliders_applet (localhost:5020/bokeh/sliders/)

  bokeh-server --port=5020 --ws-port=5021 --backend=memory --zmqaddr="tcp://127.0.0.1:5620" --script=sliders_app.py

* examples/app/stock_applet (localhost:5030/bokeh/stocks/)

  bokeh-server --port=5030 --ws-port=5031 --backend=memory --zmqaddr="tcp://127.0.0.1:5630" --script=stock_app.py

Plan for the future is to be able to start up new applets in an already running server so that running multiple servers on different ports is not necessary.

General Server Demos
====================

Run a standard server like this from the top level of the source tree:

  bokeh-server --backend=memory -D remotedata/

Now run any examples/plotting/server or examples/glyphs server or animated examples.

One good thing to do is to run animated.py and show it in the browser. Then Ctrl-Z to interrupt the process and show that the browser stop as well. Finally resume the process to show the plot animating again.

Notebook Demos
==============

Have a notebook server running in examples/glyphs and examples/plotting/notebook

Abstract Rendering
==================

There are two scripts under examples/plotting/server. Hugo's hosted taxi demo as well (see notes above, though)

Webpages
========

I open up the following:

* http://bokeh.pydata.org

  show off gallery, tutorial, also JSFiddle links in JS ref docs

* https://github.com/ContinuumIO/bokeh

  Show off download stats, etc

  NOTE: migrating to https://github.com/Bokeh/bokeh very soon (next week)

* http://nbviewer.ipython.org/github/ContinuumIO/bokeh-notebooks/blob/master/index.ipynb

  Show off tutorial notebooks, intro notebook, etc.

Spectrogram
===========

This demo only runs on a laptop with a working pyaudio. I have not had success except on OSX, so YMMV. First build all of BokehJS (I like to do a "grunt deploy copy" in the bokehjs dir). Then from bokehjs/build/demo/spectrogram, run:

  python soundserver_threaded.py

and navigate to localhost:5000

NOTE: this example is currently busted in master from recent big refactor, will be fixed shortly, please use latest release tag if necessary.

Work is ongoing to make this example much easier and simpler to run, as well as robust.
