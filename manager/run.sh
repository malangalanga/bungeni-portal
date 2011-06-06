export JYTHON_PATH=$1
export CLASSPATH=./lib/dom4j-1.6.1.jar:./lib/jaxen-1.1.3.jar:./lib/miglayout-3.7.4-swing.jar
java -cp $JYTHON_PATH:$CLASSPATH org.python.util.jython ./src/manager.py $2
