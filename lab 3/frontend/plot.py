import matplotlib.pyplot as plt
from matplotlib.pyplot import show, plot,draw
import mpld3
import numpy as np
import re
import json
from bottle import template
import sys


replacements = {
    'sin' : 'np.sin',
    'cos' : 'np.cos',
    'exp': 'np.exp',
    'sqrt': 'np.sqrt',
    '^': '**',
}

allowed_words = [
    'x',
    'sin',
    'cos',
    'sqrt',
    'exp',
]

def string2func(string):
    ''' evaluates the string and returns a function of x '''
    # find all words and check if all are allowed:
    for word in re.findall('[a-zA-Z_]+', string):
        if word not in allowed_words:
            raise ValueError(
                '"{}" is forbidden to use in math expression'.format(word)
            )

    for old, new in replacements.items():
        string = string.replace(old, new)

    def func(x):
        return eval(string)

    return func

def myplotfunc(str):
    try:
        func = string2func(str)

        x = np.linspace(-25, 25, 500)



        fig = plt.figure()
        plt.plot(x, func(x))
        #plot = figure()

        #plot.line(x=x, y=func(x))
        #html = file_html(plot, CDN, "my plot")
        #mpld3.fig_to_html(fig, template_type="simple")
        mpld3.save_html(fig,"ploot.html")
        ploot = open("ploot.html", "r")
        ploot = " ".join(ploot.readlines())

        #myhtml=open('plot.html','w')
        #myhtml.write(html)
        #myhtml.close()

        mathplot = open("mathplot.html", "r")
        mathplot=" ".join(mathplot.readlines())
        returnhome = open("returntohome.html", "r")
        returnhome = " ".join(returnhome.readlines())


          #print mathplot
        finalstr = mathplot + ploot + returnhome+'</html>'
        #print finalstr
        finalplot=open('finalplot.html', 'w')
        finalplot.write(finalstr)


        return True
    except:
       print "Unexpected error:", sys.exc_info()[0] 

       print "LOLahaha"
    #mpld3.save_html(fig, "test.html")
       return False
