# [CSC326-Programming-Languages](http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html)

Detailed Lab Instructions visit: https://www.eecg.utoronto.ca/~jzhu/csc326/csc326.html

### Course Objective
General introduction of modern programming languages and paradigms, including imperative programming, object-oriented programming, aspect-oriented programming, functional programming, and concurrent programming. The course will be supplimented by hands-on practice of web programming utilizing a multitude of programming paradigms with the syntactical versatility of Python.

## Description	
In this project, you are challenged to create a website that mimics Google's search engine.

A description of search engine's architecture is covered in the lecture note. A reference of Google's original page rank algorithm can be found at here. Section 2 is the relevant section.

 
## Requirement	
 
#### Frontend:
Your frontend should present a simple query interface to the web user, which asks for a single keyword. In response to a user query through a web browser, the frontend should respond by searching the keyword against the indexed database of URLs built by the backend. In addition, the returned URL should be displayed in sorted order according to a ranked score computed in advance by the backend.
 
#### Backend:
Your backend should take an arbitrary file named urllist.txt, which contains one URL per line, and build an inverted index database which maps keyward to URLs. In addition, each URL needs to be assigned a page rank using page rank algorithm.
 
## Resource	
 
#### Frontend:
You should use the Bottle web framework, which was covered in the tutorial.
 
#### Backend:
Your backend should take an arbitrary file named urllist.txt, which contains one URL per line, and build an inverted index database which maps keywords to URLs. In addition, each URL needs to be assigned a page rank using PageRank algorithm.
You are provided a reference implementation of the Crawler crawler.py, which can recursively visit the URLs, preprocess it so that a word list of each URLs are returned. In addition, the link relationship between the URLs are also discovered. You can build the backend by modifying file so that a persistent database, including both the reverse index and rank scores, is built and used by the frontend.

You are also provided a reference implementation of the Page rank algorithm pagerank.py.

## Batteries
The external packages that these facilities depend on, are pre-installed for you on the ugsparc systems. You are welcome to use other packages of your preference, but you are on your own for installation.
 
## Logistics
One or two member will be responsible for the web frontend.

One or two member will be responsible for the web backend.

Depending on preference, one dedicated member should be assigned the role of unit testing and packaging, and one dedicated person should be assigned the role of documenting the final design and test result.
 
## Deliverables
The project is to be completed in four lab stages.
